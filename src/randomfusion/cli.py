import click
from .core import get_key_data, remap_fingerprint
# Update imports from visuals
from .visuals.procedural import (
        generate_color_blocks, 
        generate_concentric_circles, 
        generate_noisescape,
        generate_mandelbrot
    )
from PIL import Image

# Define available visual styles
VISUAL_STYLES = {
    "color_blocks": generate_color_blocks,
    "circles": generate_concentric_circles,
    "noisescape": generate_noisescape,
    "mandelbrot": generate_mandelbrot
}

@click.group()
def cli():
    """
    RandomFusion: Generates unique visual art from cryptographic key fingerprints.
    """
    pass

@cli.command()
@click.argument('key_input', type=str)
@click.option('--output', '-o', default='randomfusion_output.png', help='Output image file name.', show_default=True)
@click.option('--width', type=int, default=256, help='Width of the output image.', show_default=True)
@click.option('--height', type=int, default=256, help='Height of the output image.', show_default=True)
@click.option(
    '--style', 
    type=click.Choice(list(VISUAL_STYLES.keys()), case_sensitive=False), 
    default='color_blocks', 
    help='Visual style to generate.',
    show_default=True
)
# Parameters specific to color_blocks
@click.option('--grid-size', type=int, default=8, help='[color_blocks] Blocks per row/column.', show_default=True)
# Parameters specific to circles (can add more later if needed)
@click.option('--num-circles', type=int, default=None, help='[circles] Override number of circles (default is seed-derived).')
@click.option('--base-stroke', type=int, default=None, help='[circles] Override base stroke width (default is seed-derived).')

def generate(
    key_input: str, output: str, width: int, height: int, style: str,
    grid_size: int, num_circles: int, base_stroke: int
):
    """
    Generates a visual fingerprint from a KEY_INPUT.

    KEY_INPUT can be a path to an SSH public key file or a raw fingerprint string.
    """
    click.echo(f"RandomFusion CLI starting generation...")
    click.echo(f"Processing key input: {key_input}")
    click.echo(f"Target output image: {output} (Size: {width}x{height}, Style: {style})")

    try:
        fingerprint_data = get_key_data(key_input)
        click.echo(f"Successfully obtained fingerprint data: {fingerprint_data}")

        remapped_data = remap_fingerprint(fingerprint_data)
        click.echo(f"Data remapped for visual generation: {remapped_data}")

        generator_func = VISUAL_STYLES[style.lower()]
        
        # Prepare arguments for the selected generator
        gen_args = {
            "seed_hex_string": remapped_data,
            "image_width": width,
            "image_height": height,
        }

        if style.lower() == "color_blocks":
            click.echo(f"Using color_blocks specific arg: grid_size={grid_size}")
            gen_args["grid_size"] = grid_size
        elif style.lower() == "circles":
            # Pass through overrides if provided, otherwise procedural generator uses its defaults or seed-derived values
            circle_params_echo = []
            if num_circles is not None:
                gen_args["default_num_circles"] = num_circles # This will override the seed-derived one
                circle_params_echo.append(f"num_circles_override={num_circles}")
            if base_stroke is not None:
                gen_args["default_base_stroke"] = base_stroke # This will override the seed-derived one
                circle_params_echo.append(f"base_stroke_override={base_stroke}")
            if circle_params_echo:
                click.echo(f"Using circles specific args: {', '.join(circle_params_echo)}")


        click.echo(f"Generating procedural image ('{style}')...")
        image = generator_func(**gen_args)

        image.save(output)
        click.secho(f"Success! Image saved to '{output}'.", fg="green")

        # Optional: try to open the image (code from previous step if you added it)

    except click.ClickException as e:
        raise
    except (ValueError, Image.DecompressionBombError, TypeError) as e_img: # Added TypeError for bad kwargs
        click.secho(f"Error during image generation or saving: {e_img}", fg="red", err=True)
        raise click.ClickException(f"Image processing error: {e_img}")
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red", err=True)
        # import traceback
        # traceback.print_exc()
        raise click.ClickException(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    cli()
