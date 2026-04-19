"""CLI commands for env file version tracking."""
import os
import click
from datetime import datetime
from envoy_cli.version import record_version, list_versions, get_version, delete_versions, VersionError

_BASE_DIR = os.environ.get("ENVOY_STORE_DIR", os.path.expanduser("~/.envoy"))


@click.group("version")
def version_group():
    """Track and restore env file versions."""


@version_group.command("record")
@click.argument("env_name")
@click.argument("content")
@click.option("--message", "-m", default="", help="Version message")
def record_cmd(env_name: str, content: str, message: str):
    """Record a new version of an env file."""
    try:
        entry = record_version(_BASE_DIR, env_name, content, message)
        click.echo(f"Recorded version {entry['version']} for '{env_name}'")
    except VersionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@version_group.command("list")
@click.argument("env_name")
def list_cmd(env_name: str):
    """List all versions of an env file."""
    versions = list_versions(_BASE_DIR, env_name)
    if not versions:
        click.echo(f"No versions found for '{env_name}'")
        return
    for v in versions:
        ts = datetime.fromtimestamp(v["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        msg = f" — {v['message']}" if v["message"] else ""
        click.echo(f"v{v['version']}  {ts}{msg}")


@version_group.command("show")
@click.argument("env_name")
@click.argument("number", type=int)
def show_cmd(env_name: str, number: int):
    """Show content of a specific version."""
    try:
        v = get_version(_BASE_DIR, env_name, number)
        click.echo(v["content"])
    except VersionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@version_group.command("clear")
@click.argument("env_name")
def clear_cmd(env_name: str):
    """Delete all versions for an env file."""
    delete_versions(_BASE_DIR, env_name)
    click.echo(f"Cleared versions for '{env_name}'")
