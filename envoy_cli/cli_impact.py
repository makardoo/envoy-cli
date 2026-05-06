"""CLI commands for managing env impact levels."""
from __future__ import annotations

import click

from envoy_cli.impact import (
    ImpactError,
    VALID_LEVELS,
    get_impact,
    list_impact,
    remove_impact,
    set_impact,
)

_BASE = click.get_app_dir("envoy")


@click.group("impact")
def impact_group() -> None:
    """Manage impact levels for env files."""


@impact_group.command("set")
@click.argument("name")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
@click.option("--base-dir", default=_BASE, hidden=True)
def set_cmd(name: str, level: str, base_dir: str) -> None:
    """Set the impact level for NAME."""
    try:
        set_impact(base_dir, name, level.lower())
        click.echo(f"Impact level for '{name}' set to '{level.lower()}'.")
    except ImpactError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@impact_group.command("get")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def get_cmd(name: str, base_dir: str) -> None:
    """Show the impact level for NAME."""
    try:
        level = get_impact(base_dir, name)
        click.echo(level)
    except ImpactError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@impact_group.command("remove")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def remove_cmd(name: str, base_dir: str) -> None:
    """Remove the impact level entry for NAME."""
    try:
        remove_impact(base_dir, name)
        click.echo(f"Impact level for '{name}' removed.")
    except ImpactError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@impact_group.command("list")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all impact level entries."""
    entries = list_impact(base_dir)
    if not entries:
        click.echo("No impact levels set.")
        return
    for env_name, level in sorted(entries.items()):
        click.echo(f"{env_name}: {level}")
