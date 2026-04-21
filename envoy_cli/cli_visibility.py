"""CLI commands for managing env visibility settings."""

from __future__ import annotations

from pathlib import Path

import click

from envoy_cli.visibility import (
    VisibilityError,
    VALID_LEVELS,
    set_visibility,
    get_visibility,
    remove_visibility,
    list_visibility,
)

_BASE_DIR = Path.home() / ".envoy_store"


@click.group(name="visibility")
def visibility_group() -> None:
    """Manage visibility settings for env files."""


@visibility_group.command(name="set")
@click.argument("env_name")
@click.argument("level", type=click.Choice(sorted(VALID_LEVELS)))
@click.option("--base-dir", default=str(_BASE_DIR), hidden=True)
def set_cmd(env_name: str, level: str, base_dir: str) -> None:
    """Set visibility level for ENV_NAME."""
    try:
        set_visibility(Path(base_dir), env_name, level)
        click.echo(f"Visibility for '{env_name}' set to '{level}'.")
    except VisibilityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@visibility_group.command(name="get")
@click.argument("env_name")
@click.option("--base-dir", default=str(_BASE_DIR), hidden=True)
def get_cmd(env_name: str, base_dir: str) -> None:
    """Get visibility level for ENV_NAME."""
    try:
        level = get_visibility(Path(base_dir), env_name)
        click.echo(level)
    except VisibilityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@visibility_group.command(name="remove")
@click.argument("env_name")
@click.option("--base-dir", default=str(_BASE_DIR), hidden=True)
def remove_cmd(env_name: str, base_dir: str) -> None:
    """Remove visibility setting for ENV_NAME."""
    try:
        remove_visibility(Path(base_dir), env_name)
        click.echo(f"Visibility setting for '{env_name}' removed.")
    except VisibilityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@visibility_group.command(name="list")
@click.option("--base-dir", default=str(_BASE_DIR), hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all visibility settings."""
    settings = list_visibility(Path(base_dir))
    if not settings:
        click.echo("No visibility settings configured.")
        return
    for env_name, level in sorted(settings.items()):
        click.echo(f"{env_name}: {level}")
