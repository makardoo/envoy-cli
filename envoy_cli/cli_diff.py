"""CLI commands for diffing .env file versions."""

import click
from envoy_cli.storage import load_env, env_file_path
from envoy_cli.env_file import decrypt_env
from envoy_cli.diff import diff_envs, format_diff


@click.group(name="diff")
def diff_group():
    """Compare .env file versions."""


@diff_group.command(name="show")
@click.argument("env_name")
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase.")
@click.option("--show-values", is_flag=True, default=False, help="Show actual values instead of masking.")
def show_diff(env_name: str, file_a: str, file_b: str, passphrase: str, show_values: bool):
    """Show diff between two local .env files."""
    try:
        with open(file_a, "r") as f:
            content_a = f.read()
        with open(file_b, "r") as f:
            content_b = f.read()

        decrypted_a = decrypt_env(content_a, passphrase)
        decrypted_b = decrypt_env(content_b, passphrase)

        diff = diff_envs(decrypted_a, decrypted_b)
        output = format_diff(diff, mask_values=not show_values)
        click.echo(f"Diff for '{env_name}':")
        click.echo(output)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@diff_group.command(name="local")
@click.argument("env_name")
@click.argument("incoming_file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase.")
@click.option("--show-values", is_flag=True, default=False, help="Show actual values instead of masking.")
def diff_local(
    env_name: str, incoming_file: str, passphrase: str, show_values: bool
):
    """Diff a stored env against an incoming file."""
    try:
        stored_raw = load_env(env_name)
        stored_decrypted = decrypt_env(stored_raw, passphrase)

        with open(incoming_file, "r") as f:
            incoming_raw = f.read()
        incoming_decrypted = decrypt_env(incoming_raw, passphrase)

        diff = diff_envs(stored_decrypted, incoming_decrypted)
        output = format_diff(diff, mask_values=not show_values)
        click.echo(f"Diff for '{env_name}' (stored vs incoming):")
        click.echo(output)
    except FileNotFoundError:
        click.echo(f"Error: env '{env_name}' not found in local store.", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
