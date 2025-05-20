from PIL import Image, ImageDraw
import hashlib

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Converts a 6-character hex color string (e.g., 'FF0000') to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        # Fallback for unexpected length, could make it more robust
        # e.g., by padding or truncating, or deriving from a hash
        h = hashlib.sha256(hex_color.encode()).hexdigest()[:6]
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_color_blocks(
    seed_hex_string: str,
    image_width: int = 256,
    image_height: int = 256,
    grid_size: int = 8
) -> Image.Image:
    """
    Generates an image with a grid of colored blocks based on a seed hex string.
    """
    if not seed_hex_string:
        raise ValueError("Seed hex string cannot be empty.")
    if grid_size <= 0:
        raise ValueError("Grid size must be positive.")

    # Create a new image with a background color derived from the start of the seed
    # Use first 6 chars for background, or a default if seed is too short
    bg_hex = seed_hex_string[:6] if len(seed_hex_string) >= 6 else "101010" # Dark gray default
    background_color = hex_to_rgb(bg_hex)
    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    block_width = image_width // grid_size
    block_height = image_height // grid_size

    # Ensure we have enough hex characters for colors, cycle if necessary
    # Each block needs 6 chars for its color.
    num_blocks = grid_size * grid_size
    chars_needed_for_blocks = num_blocks * 6
    
    # Create a color data string by repeating/cycling the seed if it's too short
    color_data_string = seed_hex_string
    while len(color_data_string) < chars_needed_for_blocks:
        # Append a hash of the current string to extend it pseudo-randomly but deterministically
        color_data_string += hashlib.sha256(color_data_string.encode()).hexdigest()
    
    # If the seed was very short initially (less than 6 for bg), use a part of the extended one
    if len(seed_hex_string) < 6:
        background_color = hex_to_rgb(color_data_string[0:6])
        # Redraw background with potentially new color if seed was too short
        image = Image.new("RGB", (image_width, image_height), background_color)
        draw = ImageDraw.Draw(image)


    color_idx = 6 # Start after the background color portion if seed was long enough

    for row in range(grid_size):
        for col in range(grid_size):
            x0 = col * block_width
            y0 = row * block_height
            x1 = x0 + block_width
            y1 = y0 + block_height

            # Get color for this block
            if color_idx + 6 <= len(color_data_string):
                block_hex_color = color_data_string[color_idx : color_idx + 6]
                color_idx += 6
            else:
                # Should not happen if color_data_string is long enough, but as a fallback:
                block_hex_color = hashlib.sha256(f"{seed_hex_string}{row}{col}".encode()).hexdigest()[:6]
            
            block_color = hex_to_rgb(block_hex_color)
            draw.rectangle([x0, y0, x1, y1], fill=block_color, outline=None) # No outline for now

    return image
