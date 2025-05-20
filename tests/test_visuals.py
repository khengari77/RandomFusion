import pytest
from PIL import Image, ImageChops
import hashlib

# Ensure src is in path for imports if running pytest from project root
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from randomfusion.visuals.procedural import hex_to_rgb, generate_color_blocks

def test_hex_to_rgb_valid():
    assert hex_to_rgb("FF0000") == (255, 0, 0)
    assert hex_to_rgb("#00FF00") == (0, 255, 0)
    assert hex_to_rgb("0000FF") == (0, 0, 255)
    assert hex_to_rgb("123456") == (0x12, 0x34, 0x56)

def test_hex_to_rgb_malformed():
    # Fallback behavior: hashes the input and takes first 6 hex chars
    short_hex = "123"
    expected_hash_prefix = hashlib.sha256(short_hex.encode()).hexdigest()[:6]
    r, g, b = tuple(int(expected_hash_prefix[i:i+2], 16) for i in (0, 2, 4))
    assert hex_to_rgb(short_hex) == (r, g, b)

    long_hex = "123456789" # Also uses fallback
    expected_hash_prefix_long = hashlib.sha256(long_hex.encode()).hexdigest()[:6]
    r_l, g_l, b_l = tuple(int(expected_hash_prefix_long[i:i+2], 16) for i in (0, 2, 4))
    assert hex_to_rgb(long_hex) == (r_l, g_l, b_l)


def test_generate_color_blocks_runs():
    seed = "a" * 64 # A full SHA256 hex string
    img = generate_color_blocks(seed_hex_string=seed, image_width=64, image_height=64, grid_size=4)
    assert isinstance(img, Image.Image)
    assert img.size == (64, 64)

def test_generate_color_blocks_empty_seed():
    with pytest.raises(ValueError, match="Seed hex string cannot be empty"):
        generate_color_blocks(seed_hex_string="", image_width=32, image_height=32, grid_size=2)

def test_generate_color_blocks_invalid_grid_size():
    with pytest.raises(ValueError, match="Grid size must be positive"):
        generate_color_blocks(seed_hex_string="123456", grid_size=0)
    with pytest.raises(ValueError, match="Grid size must be positive"):
        generate_color_blocks(seed_hex_string="123456", grid_size=-1)

def test_generate_color_blocks_determinism():
    """Crucial test: ensure the same input produces the exact same image."""
    seed1 = "abcdef1234567890" * 4 # 64 chars
    seed2 = "abcdef1234567890" * 4 # Same seed

    img1 = generate_color_blocks(seed_hex_string=seed1, image_width=32, image_height=32, grid_size=2)
    img2 = generate_color_blocks(seed_hex_string=seed2, image_width=32, image_height=32, grid_size=2)

    # Compare images pixel by pixel. diff should be None if images are identical.
    diff = ImageChops.difference(img1, img2)
    assert diff.getbbox() is None, "Images generated from the same seed are not identical"

    # Ensure different seeds produce different images
    seed3 = "0987654321fedcba" * 4 # Different seed
    img3 = generate_color_blocks(seed_hex_string=seed3, image_width=32, image_height=32, grid_size=2)
    diff_different_seed = ImageChops.difference(img1, img3)
    assert diff_different_seed.getbbox() is not None, "Images generated from different seeds are identical"

def test_generate_color_blocks_short_seed_extension():
    """Test that a short seed is extended deterministically"""
    short_seed = "abc"
    # Generate image once
    img1 = generate_color_blocks(seed_hex_string=short_seed, image_width=16, image_height=16, grid_size=2)
    
    # Generate image again with the same short seed
    img2 = generate_color_blocks(seed_hex_string=short_seed, image_width=16, image_height=16, grid_size=2)

    diff = ImageChops.difference(img1, img2)
    assert diff.getbbox() is None, "Short seed extension is not deterministic"

    # Check that the background is also consistent if derived from the extended seed
    # The current logic re-draws background if seed was < 6 chars initially, using the extended string.
    # This implicitly tests that part.
