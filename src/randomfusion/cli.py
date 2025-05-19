import click
from .core import get_key_data, remap_fingerprint # Import new functions

@click.group()
def cli():
    """
    RandomFusion: Generates unique visual art from cryptographic key fingerprints.
    """
    pass

@cli.command()
@click.argument('key_input', type=str)
@click.option('--output', '-o', default='randomfusion_output.png', help='Output image file name.', show_default=True)
def generate(key_input: str, output: str):
    """
    Generates a visual fingerprint from a KEY_INPUT.

    KEY_INPUT can be a path to an SSH public key file or a raw fingerprint string.
    """
    click.echo(f"RandomFusion CLI starting generation...")
    click.echo(f"Processing key input: {key_input}")
    click.echo(f"Target output image: {output}")

    try:
        # (F1.2) Input handling & (F1.3) Fingerprint extraction
        fingerprint_data = get_key_data(key_input)
        click.echo(f"Successfully obtained fingerprint data: {fingerprint_data}")

        # (F1.4) Avalanche Remapping
        remapped_data = remap_fingerprint(fingerprint_data)
        click.echo(f"Data remapped for visual generation: {remapped_data}")

        # Placeholder for (F1.5) Procedural Image Generation
        click.echo(f">>> Placeholder: Visual generation using '{remapped_data}' to create '{output}'...")
        # For now, let's create a dummy file to signify completion
        with open(output, 'w') as f:
            f.write(f"Visual for: {remapped_data}\n")
        click.secho(f"Success! Dummy output saved to '{output}'. Replace with actual image generation.", fg="green")

    except click.ClickException as e:
        # Errors raised by click.ClickException in core.py will be handled nicely
        raise # Re-raise to let Click handle it
    except Exception as e:
        # Catch any other unexpected errors
        click.secho(f"An unexpected error occurred: {e}", fg="red", err=True)
        # Optionally, re-raise if you want a stack trace for debugging,
        # or raise a click.ClickException for a cleaner exit.
        raise click.ClickException(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    cli()
