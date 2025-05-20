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


def generate_concentric_circles(
    seed_hex_string: str,
    image_width: int = 256,
    image_height: int = 256,
    default_num_circles: int = 10, # Default if seed doesn't specify well
    default_base_stroke: int = 2   # Default if seed doesn't specify well
) -> Image.Image:
    """
    Generates an image with concentric circles based on a seed hex string.
    """
    if not seed_hex_string:
        raise ValueError("Seed hex string cannot be empty.")

    # --- 1. Derive Parameters from Seed ---
    current_seed_pos = 0
    seed_len = len(seed_hex_string)

    def get_seed_chunk(length: int, advance_pos: bool = True) -> str:
        nonlocal current_seed_pos
        if seed_len == 0: return "0" * length # Should not happen if initial check passes
        
        # Cycle through seed if not enough characters
        chunk = ""
        for _ in range(length):
            chunk += seed_hex_string[current_seed_pos % seed_len]
            if advance_pos:
                current_seed_pos +=1 # Advance for next distinct char, even if cycling overall string
        return chunk

    # Background Color
    bg_hex = get_seed_chunk(6)
    background_color = hex_to_rgb(bg_hex)
    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    # Number of Circles
    num_circles_hex = get_seed_chunk(2)
    try:
        # Map 00-FF (0-255) to a reasonable range, e.g., 5 to 30 circles
        num_circles = 5 + (int(num_circles_hex, 16) % 26) # 5 to 30
    except ValueError:
        num_circles = default_num_circles
    if num_circles <= 0: num_circles = default_num_circles


    # Base Stroke Width
    base_stroke_hex = get_seed_chunk(2)
    try:
        # Map 00-FF (0-255) to a reasonable range, e.g., 1 to 8 pixels
        base_stroke_width = 1 + (int(base_stroke_hex, 16) % 8)
    except ValueError:
        base_stroke_width = default_base_stroke
    if base_stroke_width <=0: base_stroke_width = default_base_stroke


    # --- 2. Drawing Logic ---
    center_x = image_width // 2
    center_y = image_height // 2
    
    # Max radius the largest circle can have
    # (leaving a small margin from the edge)
    max_allowable_radius = (min(image_width, image_height) / 2.0) * 0.95 
    
    if num_circles == 0: # Should be caught by earlier check, but defensive
        return image

    # Draw circles from largest to smallest
    for i in range(num_circles, 0, -1):
        # Radius: proportionally smaller for inner circles
        # The i-th circle (from outside, 1-indexed where largest is num_circles)
        radius_factor = i / num_circles
        radius = max_allowable_radius * radius_factor

        # Color for this circle
        circle_color_hex = get_seed_chunk(6)
        circle_color = hex_to_rgb(circle_color_hex)

        # Stroke width variation for this circle
        stroke_variation_hex = get_seed_chunk(1) # Get 1 hex char (0-F)
        try:
            # Add a small variation (e.g., 0-3 pixels) to the base
            stroke_variation = int(stroke_variation_hex, 16) % 4 
        except ValueError:
            stroke_variation = 0
        
        current_stroke_width = max(1, base_stroke_width + stroke_variation - (num_circles - i)//3 ) # Thinner for inner circles
        current_stroke_width = max(1, current_stroke_width) # Ensure at least 1

        # Define bounding box for the circle
        # Ellipse needs (x0, y0, x1, y1)
        x0 = center_x - radius
        y0 = center_y - radius
        x1 = center_x + radius
        y1 = center_y + radius
        
        # Pillow's ellipse draws a filled ellipse if fill is given.
        # To draw an outline (a circle), we specify outline and width, and no fill.
        if radius > current_stroke_width / 2 : # Only draw if radius is sensible for stroke
            draw.ellipse(
                (x0, y0, x1, y1),
                outline=circle_color,
                width=current_stroke_width
            )
        # Alternative: draw filled circles, largest first, then smaller ones on top.
        # This might be simpler than managing stroke widths for very thin circles.
        # For now, using outline.

    return image
