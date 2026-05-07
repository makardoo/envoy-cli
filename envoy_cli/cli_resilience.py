"""CLI commands for resilience level management."""
import os
import click
from envoy_cli.resilience import (
    ResilienceError,
    VALID_LEVELS,
    set_resilience,
    get_resilience,
    remove_resilience,
    list_resilience,
)

_BASE = os.environ.get("ENVOY_HOME", os.path.expanduser("~/.envoy"))


@click.group("resilience")
def resilience_group():
    """Manage resilience levels for env files."""


@resilience_group.command("set")
@click.argument("name")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--base-dir", default=_BASE, hidden=True)
def set_cmd(name: str, level: str, base_dir: str):
    """Set the resilience LEVEL for env NAME."""
    try:
        set_resilience(base_dir, name, level)
        click.echo(f"Resilience for '{name}' set to '{level}'.")
    except ResilienceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@resilience_group.command("get")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def get_cmd(name: str, base_dir: str):
    """Show the resilience level for env NAME."""
    try:
        level = get_resilience(base_dir, name)
        click.echo(level)
    except ResilienceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@resilience_group.command("remove")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def remove_cmd(name: str, base_dir: str):
    """Remove the resilience record for env NAME."""
    try:
        remove_resilience(base_dir, name)
        click.echo(f"Resilience record for '{name}' removed.")
    except ResilienceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@resilience_group.command("list")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(base_dir: str):
    """List all resilience records."""
    records = list_resilience(base_dir)
    if not records:
        click.echo("No resilience records found.")
        return
    for name, level in sorted(records.items()):
        click.echo(f"{name}: {level}")
