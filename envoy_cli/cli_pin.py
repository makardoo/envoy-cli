"""CLI commands for pinning env snapshots."""
import os
import click
from envoy_cli.pin import pin_env, get_pin, remove_pin, list_pins, PinError

_base_dir = os.environ.get("ENVOY_BASE_DIR", os.path.expanduser("~/.envoy"))


@click.group("pin")
def pin_group():
    """Pin env versions to specific snapshots."""


@pin_group.command("set")
@click.argument("env_name")
@click.argument("snapshot_id")
@click.option("--label", default="", help="Optional human-readable label.")
def set_pin(env_name, snapshot_id, label):
    """Pin ENV_NAME to SNAPSHOT_ID."""
    try:
        pin_env(_base_dir, env_name, snapshot_id, label or None)
        click.echo(f"Pinned '{env_name}' to snapshot '{snapshot_id}'.")
    except PinError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pin_group.command("show")
@click.argument("env_name")
def show_pin(env_name):
    """Show the pinned snapshot for ENV_NAME."""
    try:
        info = get_pin(_base_dir, env_name)
        click.echo(f"env:      {env_name}")
        click.echo(f"snapshot: {info['snapshot_id']}")
        if info['label']:
            click.echo(f"label:    {info['label']}")
    except PinError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pin_group.command("remove")
@click.argument("env_name")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def remove_pin_cmd(env_name, yes):
    """Remove the pin for ENV_NAME."""
    if not yes:
        click.confirm(f"Remove pin for '{env_name}'?", abort=True)
    try:
        remove_pin(_base_dir, env_name)
        click.echo(f"Removed pin for '{env_name}'.")
    except PinError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pin_group.command("list")
def list_all():
    """List all pinned envs."""
    pins = list_pins(_base_dir)
    if not pins:
        click.echo("No pins defined.")
        return
    for p in pins:
        label = f"  [{p['label']}]" if p['label'] else ""
        click.echo(f"{p['env_name']:20s} -> {p['snapshot_id']}{label}")
