import pytest
import subprocess
from unittest.mock import patch, MagicMock
import os
from pathlib import Path

# Ensure src is in path for imports if running pytest from project root
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from randomfusion.core import (
    get_fingerprint_from_file,
    normalize_fingerprint_string,
    get_key_data,
    remap_fingerprint,
    FINGERPRINT_REGEX
)
import click # For click.ClickException

# Path to the test assets directory
TEST_ASSETS_DIR = Path(__file__).parent / "assets"
VALID_TEST_KEY_PUB_FILE = TEST_ASSETS_DIR / "test_key_for_pytest.pub"
# Replace with the ACTUAL fingerprint from your generated test_key_for_pytest.pub
# Example: ssh-keygen -E sha256 -lf tests/assets/test_key_for_pytest.pub
# Output might be: 255 SHA256:qL7x5Y+7Q8zRbk/yYk6xN8zW3kH9jF0oD7rX5mN6zC0 pytest_key@randomfusion (ED25519)
EXPECTED_FINGERPRINT_SHA256 = "SHA256:5Ba/N0m20dEelWi1fAtNdSd48HUhIBhILLG5cOP8POg"

# Create the dummy key file if it doesn't exist (e.g., in CI)
# This is a bit of a hack for pytest; ideally, the key is version controlled or built.
# For this exercise, we'll assume it's checked in or we create it.
# We will check it in tests/assets/
if not VALID_TEST_KEY_PUB_FILE.exists():
    # This is a fallback if not checked in; better to check it in.
    print(f"Warning: Test key file {VALID_TEST_KEY_PUB_FILE} not found. Tests involving it might fail or be skipped.")
    # One could add code here to generate it using ssh-keygen if strictly necessary for a test run
    # For now, we assume it's present.

@pytest.fixture
def mock_subprocess_run():
    with patch('subprocess.run') as mock_run:
        yield mock_run

def test_get_fingerprint_from_file_success(mock_subprocess_run):
    if not VALID_TEST_KEY_PUB_FILE.exists():
        pytest.skip(f"Test key file {VALID_TEST_KEY_PUB_FILE} not found, skipping test.")

    mock_result = MagicMock()
    mock_result.stdout = f"2048 {EXPECTED_FINGERPRINT_SHA256} user@host (RSA)\n" # Mock output
    mock_result.stderr = ""
    mock_subprocess_run.return_value = mock_result

    fingerprint = get_fingerprint_from_file(str(VALID_TEST_KEY_PUB_FILE))
    assert fingerprint == EXPECTED_FINGERPRINT_SHA256
    mock_subprocess_run.assert_any_call(
        ['ssh-keygen', '-l', '-f', str(VALID_TEST_KEY_PUB_FILE), '-E', 'sha256'],
        capture_output=True, text=True, check=True
    )

def test_get_fingerprint_from_file_fallback_success(mock_subprocess_run):
    if not VALID_TEST_KEY_PUB_FILE.exists():
        pytest.skip(f"Test key file {VALID_TEST_KEY_PUB_FILE} not found, skipping test.")

    # First call (with -E sha256) fails, second call (fallback) succeeds
    mock_failure_result = subprocess.CalledProcessError(1, "cmd", stderr="simulated error with -E")
    mock_success_result = MagicMock()
    mock_success_result.stdout = f"2048 {EXPECTED_FINGERPRINT_SHA256} user@host (RSA)\n"
    mock_success_result.stderr = ""
    
    # Configure the mock to raise an exception on the first call, return success on the second
    mock_subprocess_run.side_effect = [mock_failure_result, mock_success_result]

    fingerprint = get_fingerprint_from_file(str(VALID_TEST_KEY_PUB_FILE))
    assert fingerprint == EXPECTED_FINGERPRINT_SHA256
    assert mock_subprocess_run.call_count == 2
    mock_subprocess_run.assert_any_call(
        ['ssh-keygen', '-l', '-f', str(VALID_TEST_KEY_PUB_FILE), '-E', 'sha256'],
        capture_output=True, text=True, check=True
    )
    mock_subprocess_run.assert_any_call(
        ['ssh-keygen', '-l', '-f', str(VALID_TEST_KEY_PUB_FILE)],
        capture_output=True, text=True, check=True
    )


def test_get_fingerprint_from_file_not_found():
    with pytest.raises(click.ClickException, match="Error: Key file not found"):
        get_fingerprint_from_file("non_existent_file.pub")

def test_get_fingerprint_from_file_ssh_keygen_error(mock_subprocess_run):
    if not VALID_TEST_KEY_PUB_FILE.exists():
        pytest.skip(f"Test key file {VALID_TEST_KEY_PUB_FILE} not found, skipping test.")
        
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="ssh-keygen failed")
    with pytest.raises(click.ClickException, match="Error running 'ssh-keygen"):
        get_fingerprint_from_file(str(VALID_TEST_KEY_PUB_FILE))
        
def test_get_fingerprint_from_file_ssh_keygen_not_found(mock_subprocess_run):
    if not VALID_TEST_KEY_PUB_FILE.exists():
        pytest.skip(f"Test key file {VALID_TEST_KEY_PUB_FILE} not found, skipping test.")

    mock_subprocess_run.side_effect = FileNotFoundError("ssh-keygen not found")
    with pytest.raises(click.ClickException, match="Error: 'ssh-keygen' command not found"):
        get_fingerprint_from_file(str(VALID_TEST_KEY_PUB_FILE))


def test_normalize_fingerprint_string_valid():
    fp_sha256 = EXPECTED_FINGERPRINT_SHA256
    fp_md5 = "MD5:11:22:33:44:55:66:77:88:99:aa:bb:cc:dd:ee:ff:00"
    assert normalize_fingerprint_string(fp_sha256) == fp_sha256
    assert normalize_fingerprint_string(fp_md5) == fp_md5

def test_normalize_fingerprint_string_invalid():
    with pytest.raises(click.ClickException, match="does not look like a recognized SSH fingerprint"):
        normalize_fingerprint_string("invalid_fingerprint_string")

@patch('randomfusion.core.get_fingerprint_from_file')
def test_get_key_data_file_input(mock_get_fp_from_file):
    if not VALID_TEST_KEY_PUB_FILE.exists():
        # Create a dummy file just for path existence check by get_key_data
        VALID_TEST_KEY_PUB_FILE.touch() 
        created_dummy = True
    else:
        created_dummy = False

    mock_get_fp_from_file.return_value = EXPECTED_FINGERPRINT_SHA256
    result = get_key_data(str(VALID_TEST_KEY_PUB_FILE))
    assert result == EXPECTED_FINGERPRINT_SHA256
    mock_get_fp_from_file.assert_called_once_with(str(VALID_TEST_KEY_PUB_FILE))

    if created_dummy:
        VALID_TEST_KEY_PUB_FILE.unlink() # Clean up dummy file

def test_get_key_data_fingerprint_input():
    fp_sha256 = EXPECTED_FINGERPRINT_SHA256
    assert get_key_data(fp_sha256) == fp_sha256

def test_get_key_data_invalid_input():
    with pytest.raises(click.ClickException, match="is not a valid key file path nor a recognized fingerprint string"):
        get_key_data("completely_invalid_input_akjshgd")

def test_remap_fingerprint():
    input_fp = EXPECTED_FINGERPRINT_SHA256
    expected_remapped = "d0c61f08d04699a6befe964258c375f4a6cc28cc5ba363dfaf1a636e5be6ef92"
    assert remap_fingerprint(input_fp) == expected_remapped

    input_fp_2 = "SHA256:anotherTestInputString123"
    # echo -n "SHA256:anotherTestInputString123" | sha256sum
    expected_remapped_2 = "2a3c3e5af9ee1ca90f27dc6f631415352399a15f81b3c2837e6245b3bbeb6ccc"
    assert remap_fingerprint(input_fp_2) == expected_remapped_2

    # Test that slightly different inputs produce different outputs
    assert remap_fingerprint(input_fp) != remap_fingerprint(input_fp_2)
