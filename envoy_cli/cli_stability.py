"""CLI commands for stability management."""
import click

from envoy_cli.stability import (
    StabilityError,
    VALID_LEVELS,
    get_stability,
    list_stability,
    remove_stability,
    set_stability,
)

_BASE = click.get_app_dir("envoy")


@click.group(name="stability")
def stability_group():
    """Manage env stability levels."""


@stability_group.command("set")
@click.argument("name")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--base-dir", default=_BASE, hidden=True)
def set_cmd(name: str, level: str, base_dir: str) -> None:
    """Set the stability level for NAME."""
    try:
        set_stability(base_dir, name, level)
        click.echo(f"Stability for '{name}' set to '{level}'.")
    except StabilityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@stability_group.command("get")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def get_cmd(name: str, base_dir: str) -> None:
    """Show the stability level for NAME."""
    try:
        level = get_stability(base_dir, name)
        click.echo(level)
    except StabilityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@stability_group.command("remove")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def remove_cmd(name: str, base_dir: str) -> None:
    """Remove the stability record for NAME."""
    try:
        remove_stability(base_dir, name)
        click.echo(f"Stability record for '{name}' removed.")
    except StabilityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@stability_group.command("list")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all stability levels."""
    data = list_stability(base_dir)
    if not data:
        click.echo("No stability records found.")
        return
    for name, level in sorted(data.items()):
        click.echo(f"{name}: {level}")
