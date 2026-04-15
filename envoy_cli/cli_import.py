"""CLI commands for importing .env files into envoy-cli."""

import click
from envoy_cli.import_env import import_from_file, merge_envs, SUPPORTED_FORMATS
from envoy_cli.env_file import serialize_env, encrypt_env
from envoy_cli.storage import save_env, load_env
from envoy_cli.audit import append_audit_entry


@click.group(name="import")
def import_group():
    """Import .env files from external sources."""


@import_group.command(name="file")
@click.argument("env_name")
@click.argument("filepath")
@click.option("--passphrase", prompt=True, hide_input=True, help="Encryption passphrase")
@click.option(
    "--format", "fmt",
    type=click.Choice(SUPPORTED_FORMATS),
    default=None,
    help="Force input file format (auto-detected if omitted)",
)
@click.option(
    "--merge",
    type=click.Choice(["override", "keep", "none"]),
    default="none",
    help="Merge strategy if env already exists (default: none = error if exists)",
)
def import_file(env_name, filepath, passphrase, fmt, merge):
    """Import FILEPATH as ENV_NAME, encrypting with PASSPHRASE."""
    try:
        incoming = import_from_file(filepath, fmt=fmt)
    except FileNotFoundError as e:
        raise click.ClickException(str(e))
    except ValueError as e:
        raise click.ClickException(str(e))

    if merge != "none":
        try:
            existing_raw = load_env(env_name)
            from envoy_cli.env_file import decrypt_env, parse_env
            decrypted = decrypt_env(existing_raw, passphrase)
            existing_pairs = parse_env(decrypted)
            existing_dict = dict(existing_pairs)
            incoming = merge_envs(existing_dict, incoming, strategy=merge)
        except FileNotFoundError:
            pass  # No existing env, just use incoming
        except Exception as e:
            raise click.ClickException(f"Failed to merge with existing env: {e}")

    env_lines = "\n".join(f"{k}={v}" for k, v in incoming.items())
    encrypted = encrypt_env(env_lines, passphrase)
    save_env(env_name, encrypted)
    append_audit_entry(env_name, "import", {"filepath": filepath, "keys": len(incoming)})
    click.echo(f"Imported {len(incoming)} key(s) into '{env_name}'.")
