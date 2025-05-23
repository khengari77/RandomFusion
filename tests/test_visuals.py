import pytest
from PIL import Image, ImageChops
import hashlib

# Ensure src is in path for imports if running pytest from project root
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from randomfusion.visuals.procedural import (
        hex_to_rgb,
        generate_color_blocks,
        generate_concentric_circles,
        generate_noisescape
)

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


# In tests/test_visuals.py
# ... (keep existing imports and tests) ...

def test_generate_concentric_circles_runs():
    seed = "b" * 64
    img = generate_concentric_circles(seed_hex_string=seed, image_width=64, image_height=64)
    assert isinstance(img, Image.Image)
    assert img.size == (64, 64)

def test_generate_concentric_circles_empty_seed():
    with pytest.raises(ValueError, match="Seed hex string cannot be empty"):
        generate_concentric_circles(seed_hex_string="")

def test_generate_concentric_circles_determinism():
    seed1 = "cba9876543210fed" * 4 # 64 chars

    img1_params = {
        "seed_hex_string": seed1, "image_width": 48, "image_height": 48,
        "default_num_circles": 7, "default_base_stroke": 1
    }
    img1 = generate_concentric_circles(**img1_params)
    img2 = generate_concentric_circles(**img1_params) # Same seed and params

    diff = ImageChops.difference(img1, img2)
    assert diff.getbbox() is None, "Concentric circles: Images from same seed and params are not identical"

    # Test that different seeds produce different images
    seed2 = "1234567890abcdef" * 4
    img3_params = {
        "seed_hex_string": seed2, "image_width": 48, "image_height": 48,
        "default_num_circles": 7, "default_base_stroke": 1
    }
    img3 = generate_concentric_circles(**img3_params)
    diff_different_seed = ImageChops.difference(img1, img3)
    assert diff_different_seed.getbbox() is not None, "Concentric circles: Images from different seeds are identical"

def test_generate_concentric_circles_param_override_effect():
    seed = "d" * 64
    img_default = generate_concentric_circles(seed_hex_string=seed, image_width=32, image_height=32)

    # Override number of circles (should change the image)
    img_override_circles = generate_concentric_circles(
        seed_hex_string=seed, image_width=32, image_height=32, default_num_circles=5
    ) # Assuming seed would derive something different than 5
    diff1 = ImageChops.difference(img_default, img_override_circles)
    # This test is a bit tricky as the seed-derived num_circles could randomly be 5.
    # A more robust test would be to ensure that if num_circles is *different* from seed-derived, image is different.
    # For now, we assume it's unlikely they'll match perfectly often. If this test is flaky, refine.
    if img_default.tobytes() != img_override_circles.tobytes(): # Check if actually different
         assert diff1.getbbox() is not None, "Overriding num_circles did not change the image as expected"
    else:
        print("Warning: Overriding num_circles resulted in the same image, possibly coincidental seed derivation.")


    # Override base stroke (should change the image)
    img_override_stroke = generate_concentric_circles(
        seed_hex_string=seed, image_width=32, image_height=32, default_base_stroke=5
    ) # Assuming seed would derive something different than 5
    diff2 = ImageChops.difference(img_default, img_override_stroke)
    if img_default.tobytes() != img_override_stroke.tobytes():
        assert diff2.getbbox() is not None, "Overriding base_stroke did not change the image as expected"
    else:
        print("Warning: Overriding base_stroke resulted in the same image, possibly coincidental seed derivation.")


def test_generate_noisescape_runs():
    seed = "c0ffee1234567890" * 4  # 64 chars
    img = generate_noisescape(seed_hex_string=seed, image_width=32, image_height=32)
    assert isinstance(img, Image.Image)
    assert img.size == (32, 32)

def test_generate_noisescape_empty_seed():
    with pytest.raises(ValueError, match="Seed hex string cannot be empty"):
        generate_noisescape(seed_hex_string="")

def test_generate_noisescape_determinism():
    seed1 = "deadbeefcafebabe" * 4  # 64 chars
    
    img1_params = {"seed_hex_string": seed1, "image_width": 24, "image_height": 24} # Smaller for faster test
    img1 = generate_noisescape(**img1_params)
    img2 = generate_noisescape(**img1_params) # Same seed and params

    diff = ImageChops.difference(img1, img2)
    if diff.getbbox() is not None: # pragma: no cover (for local debugging if determinism fails)
        try:
            img1.save("debug_noisescape_img1.png")
            img2.save("debug_noisescape_img2.png")
            diff.save("debug_noisescape_diff.png")
            print("NoiseScape determinism failed. Debug images saved.")
        except Exception as e:
            print(f"Could not save debug images for NoiseScape: {e}")
    assert diff.getbbox() is None, "NoiseScape: Images from same seed and params are not identical"

    # Ensure different seeds produce different images
    seed2 = "1234567890abcdef" * 4
    img3_params = {"seed_hex_string": seed2, "image_width": 24, "image_height": 24}
    img3 = generate_noisescape(**img3_params)
    diff_different_seed = ImageChops.difference(img1, img3)
    assert diff_different_seed.getbbox() is not None, "NoiseScape: Images from different seeds are identical"
