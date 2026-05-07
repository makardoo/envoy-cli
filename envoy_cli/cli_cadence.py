"""CLI commands for cadence management."""
from __future__ import annotations

import click

from envoy_cli.cadence import (
    CadenceError,
    VALID_CADENCES,
    get_cadence,
    list_cadences,
    remove_cadence,
    set_cadence,
)

_DEFAULT_BASE = ".envoy"


@click.group(name="cadence")
def cadence_group():
    """Manage update cadence for envs."""


@cadence_group.command("set")
@click.argument("env_name")
@click.argument("cadence", type=click.Choice(VALID_CADENCES))
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(env_name: str, cadence: str, base_dir: str) -> None:
    """Set the update cadence for ENV_NAME."""
    try:
        set_cadence(base_dir, env_name, cadence)
        click.echo(f"Cadence for '{env_name}' set to '{cadence}'.")
    except CadenceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cadence_group.command("get")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(env_name: str, base_dir: str) -> None:
    """Get the update cadence for ENV_NAME."""
    try:
        cadence = get_cadence(base_dir, env_name)
        click.echo(cadence)
    except CadenceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cadence_group.command("remove")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(env_name: str, base_dir: str) -> None:
    """Remove cadence assignment for ENV_NAME."""
    try:
        remove_cadence(base_dir, env_name)
        click.echo(f"Cadence for '{env_name}' removed.")
    except CadenceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cadence_group.command("list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all cadence assignments."""
    data = list_cadences(base_dir)
    if not data:
        click.echo("No cadences set.")
        return
    for name, cadence in sorted(data.items()):
        click.echo(f"{name}: {cadence}")
