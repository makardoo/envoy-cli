"""CLI commands for managing sensitivity classifications."""

from __future__ import annotations

import click

from envoy_cli.sensitivity import (
    VALID_LEVELS,
    SensitivityError,
    get_sensitivity,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
)

_DEFAULT_BASE = ".envoy"


@click.group(name="sensitivity")
def sensitivity_group() -> None:
    """Manage sensitivity classifications for env entries."""


@sensitivity_group.command(name="set")
@click.argument("env_name")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(env_name: str, level: str, base_dir: str) -> None:
    """Set the sensitivity level for ENV_NAME."""
    try:
        set_sensitivity(base_dir, env_name, level)
        click.echo(f"Sensitivity for '{env_name}' set to '{level}'.")
    except SensitivityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@sensitivity_group.command(name="get")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(env_name: str, base_dir: str) -> None:
    """Get the sensitivity level for ENV_NAME."""
    try:
        level = get_sensitivity(base_dir, env_name)
        click.echo(level)
    except SensitivityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@sensitivity_group.command(name="remove")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(env_name: str, base_dir: str) -> None:
    """Remove the sensitivity classification for ENV_NAME."""
    try:
        remove_sensitivity(base_dir, env_name)
        click.echo(f"Sensitivity classification for '{env_name}' removed.")
    except SensitivityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@sensitivity_group.command(name="list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all sensitivity classifications."""
    entries = list_sensitivity(base_dir)
    if not entries:
        click.echo("No sensitivity classifications set.")
        return
    for entry in entries:
        click.echo(f"{entry['env']}: {entry['level']}")
