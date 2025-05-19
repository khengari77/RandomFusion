import hashlib
import os
import re
import subprocess
import click # For click.ClickException

# Regular expression to match typical SSH fingerprint formats (SHA256 and MD5 for now)
# SHA256:SHA256:L2jqas90dpk/qNVj9L9Asjdfklj32lkjASDFLKJASDFLKJ
# MD5:16:2d:78:42:89:c1:89:ff:7c:25:0c:2a:f4:89:88:67 (legacy, but might be pasted)
FINGERPRINT_REGEX = re.compile(r"^(SHA256:[a-zA-Z0-9+/=]{43}|MD5:([0-9a-f]{2}:){15}[0-9a-f]{2})$")

def get_fingerprint_from_file(key_file_path: str) -> str:
    """
    Extracts the SHA256 fingerprint from an SSH public key file using ssh-keygen.
    """
    if not os.path.exists(key_file_path):
        raise click.ClickException(f"Error: Key file not found at '{key_file_path}'")
    if not os.path.isfile(key_file_path):
        raise click.ClickException(f"Error: '{key_file_path}' is not a file.")

    try:
        # Using -E sha256 to explicitly request SHA256 if available,
        # though -l itself often defaults to a good one.
        # Some older ssh-keygen might not support -E, so we have a fallback.
        try:
            result = subprocess.run(
                ['ssh-keygen', '-l', '-f', key_file_path, '-E', 'sha256'],
                capture_output=True, text=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e_sha256:
            # Fallback if -E sha256 fails (e.g., older ssh-keygen or if ssh-keygen not found)
            # On FileNotFoundError, the second attempt will also likely fail but gives a more generic error.
            click.echo("Warning: Could not use 'ssh-keygen -E sha256'. Trying without -E option.", err=True)
            try:
                result = subprocess.run(
                    ['ssh-keygen', '-l', '-f', key_file_path],
                    capture_output=True, text=True, check=True
                )
            except FileNotFoundError:
                 raise click.ClickException(
                    "Error: 'ssh-keygen' command not found. Please ensure it's installed and in your PATH."
                )
            except subprocess.CalledProcessError as e_fallback:
                error_message = e_fallback.stderr.strip() if e_fallback.stderr else "Unknown error with ssh-keygen."
                raise click.ClickException(
                    f"Error running 'ssh-keygen -l -f {key_file_path}': {error_message}"
                )


        # Output is like: "2048 SHA256:xxxxxxxxxxxxx user@host (RSA)"
        # Or "SHA256:xxxxxxxxxxxx user@host (RSA)" if -E is not fully supported for format string
        # Or "2048 MD5:xx:xx:xx:... user@host (RSA)"
        # We need to extract the "SHA256:xxxx..." or "MD5:xx:xx:..." part.
        output_lines = result.stdout.strip().split('\n')
        if not output_lines:
            raise click.ClickException(f"Error: 'ssh-keygen' produced no output for {key_file_path}.")

        # Try to find a line with a recognizable fingerprint
        for line in output_lines:
            parts = line.split()
            for part in parts:
                if FINGERPRINT_REGEX.match(part):
                    # Normalize: Remove "SHA256:" prefix if present, as we'll add our own remapping logic
                    # For now, let's return the full matched fingerprint string (e.g. "SHA256:xxxx")
                    return part
        
        raise click.ClickException(
            f"Error: Could not parse fingerprint from 'ssh-keygen' output for {key_file_path}.\nOutput: {result.stdout}"
        )

    except FileNotFoundError:
        raise click.ClickException(
            "Error: 'ssh-keygen' command not found. Please ensure it's installed and in your PATH."
        )
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "Unknown error with ssh-keygen."
        raise click.ClickException(
            f"Error running 'ssh-keygen -l -f {key_file_path}': {error_message}"
        )


def normalize_fingerprint_string(fp_string: str) -> str:
    """
    Validates and returns the input string if it looks like a fingerprint.
    For now, it mainly checks the format.
    """
    if FINGERPRINT_REGEX.match(fp_string):
        return fp_string
    else:
        # Could be a raw hex string for hashing, or an unsupported format
        # For now, we'll be strict. If it's not a known SSH fp format,
        # we might treat it as raw data to be hashed directly in the remapping step.
        # Let's assume for now we want a valid SSH-like fingerprint before remapping.
        raise click.ClickException(
            f"Error: Input string '{fp_string}' does not look like a recognized SSH fingerprint (SHA256 or MD5)."
        )


def get_key_data(key_input: str) -> str:
    """
    Determines if key_input is a file path or a fingerprint string.
    Returns the extracted/validated fingerprint string.
    """
    if os.path.exists(key_input) and os.path.isfile(key_input):
        click.echo(f"Input '{key_input}' detected as a file. Extracting fingerprint...")
        return get_fingerprint_from_file(key_input)
    elif FINGERPRINT_REGEX.match(key_input):
        click.echo(f"Input '{key_input}' detected as a fingerprint string.")
        return normalize_fingerprint_string(key_input) # Already matched, so this is more of a pass-through
    else:
        # A fallback for arbitrary strings that don't match file or known fingerprint format.
        # We could decide to hash this directly. For now, let's be stricter.
        raise click.ClickException(
            f"Error: Input '{key_input}' is not a valid key file path nor a recognized fingerprint string."
        )

# --- (F1.4) Avalanche Remapping will go here later ---
def remap_fingerprint(fingerprint: str) -> str:
    """
    Applies an avalanche effect by hashing the fingerprint.
    """
    # Use SHA256 for remapping, regardless of input fingerprint type
    hasher = hashlib.sha256()
    hasher.update(fingerprint.encode('utf-8'))
    remapped_hex = hasher.hexdigest()
    click.echo(f"Original fingerprint: {fingerprint}")
    click.echo(f"Remapped to (SHA256 hex): {remapped_hex}")
    return remapped_hex
