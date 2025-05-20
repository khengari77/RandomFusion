import click
from .core import get_key_data, remap_fingerprint
from .visuals.procedural import generate_color_blocks # Import the new function
from PIL import Image # To catch PIL-specific errors if necessary

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
@click.option('--grid-size', type=int, default=8, help='Number of blocks per row/column for color block visual.', show_default=True)
def generate(key_input: str, output: str, width: int, height: int, grid_size: int):
    """
    Generates a visual fingerprint from a KEY_INPUT.

    KEY_INPUT can be a path to an SSH public key file or a raw fingerprint string.
    """
    click.echo(f"RandomFusion CLI starting generation...")
    click.echo(f"Processing key input: {key_input}")
    click.echo(f"Target output image: {output} (Size: {width}x{height}, Grid: {grid_size}x{grid_size})")

    try:
        fingerprint_data = get_key_data(key_input)
        click.echo(f"Successfully obtained fingerprint data: {fingerprint_data}")

        remapped_data = remap_fingerprint(fingerprint_data)
        click.echo(f"Data remapped for visual generation: {remapped_data}")

        # (F1.5) Procedural Image Generation
        click.echo(f"Generating procedural image ('color_blocks')...")
        image = generate_color_blocks(
            seed_hex_string=remapped_data,
            image_width=width,
            image_height=height,
            grid_size=grid_size
        )

        image.save(output)
        click.secho(f"Success! Image saved to '{output}'.", fg="green")

    except click.ClickException as e:
        raise
    except (ValueError, Image.DecompressionBombError) as e_img: # Catch specific errors from Pillow or our logic
        click.secho(f"Error during image generation or saving: {e_img}", fg="red", err=True)
        raise click.ClickException(f"Image processing error: {e_img}")
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red", err=True)
        # Consider logging the full traceback here for debugging in a real app
        # import traceback
        # traceback.print_exc()
        raise click.ClickException(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    cli()
