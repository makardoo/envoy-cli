"""Command-line interface for envoy-cli using Click."""

import sys
import click

from envoy_cli.storage import save_env, load_env, list_envs, delete_env
from envoy_cli.sync import push_env, pull_env, list_remote_envs
from envoy_cli.env_file import encrypt_env, decrypt_env, load_env_file


@click.group()
@click.version_option(version="0.1.0", prog_name="envoy")
def cli():
    """envoy — manage and sync .env files securely."""
    pass


@cli.command("set")
@click.argument("env_name")
@click.argument("file", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, help="Encryption passphrase")
def set_env(env_name, file, passphrase):
    """Encrypt and store a .env file locally under ENV_NAME."""
    try:
        raw = load_env_file(file)
        encrypted = encrypt_env(raw, passphrase)
        save_env(env_name, encrypted)
        click.echo(f"✓ Stored '{env_name}' successfully.")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("get")
@click.argument("env_name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase")
@click.option("--output", "-o", type=click.Path(), default=None, help="Write to file instead of stdout")
def get_env(env_name, passphrase, output):
    """Decrypt and display (or export) a stored .env file."""
    try:
        encrypted = load_env(env_name)
        decrypted = decrypt_env(encrypted, passphrase)
        if output:
            with open(output, "w") as fh:
                fh.write(decrypted)
            click.echo(f"✓ Written to '{output}'.")
        else:
            click.echo(decrypted)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("list")
def list_local():
    """List all locally stored .env names."""
    envs = list_envs()
    if not envs:
        click.echo("No environments stored locally.")
    else:
        for name in sorted(envs):
            click.echo(f"  {name}")


@cli.command("delete")
@click.argument("env_name")
@click.confirmation_option(prompt="Are you sure you want to delete this environment?")
def remove_env(env_name):
    """Delete a locally stored .env file."""
    try:
        delete_env(env_name)
        click.echo(f"✓ Deleted '{env_name}'.")
    except FileNotFoundError:
        click.echo(f"Error: '{env_name}' not found.", err=True)
        sys.exit(1)


@cli.command("push")
@click.argument("env_name")
@click.option("--remote", default="default", show_default=True, help="Remote store path")
def push(env_name, remote):
    """Push a local .env to the remote store."""
    try:
        push_env(env_name, remote)
        click.echo(f"✓ Pushed '{env_name}' to remote '{remote}'.")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("pull")
@click.argument("env_name")
@click.option("--remote", default="default", show_default=True, help="Remote store path")
def pull(env_name, remote):
    """Pull a .env from the remote store to local."""
    try:
        pull_env(env_name, remote)
        click.echo(f"✓ Pulled '{env_name}' from remote '{remote}'.")
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("remote-list")
@click.option("--remote", default="default", show_default=True, help="Remote store path")
def remote_list(remote):
    """List .env files available on the remote store."""
    envs = list_remote_envs(remote)
    if not envs:
        click.echo("No environments found on remote.")
    else:
        for name in sorted(envs):
            click.echo(f"  {name}")


if __name__ == "__main__":
    cli()
