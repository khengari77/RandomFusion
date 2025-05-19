import click

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
    click.echo(f"RandomFusion CLI initialized.")
    click.echo(f"Received key input: {key_input}")
    click.echo(f"Output will be saved to: {output}")
    # Placeholder for actual logic
    click.echo(">>> Placeholder: Calling core logic and visual generation...")

if __name__ == '__main__':
    cli()
