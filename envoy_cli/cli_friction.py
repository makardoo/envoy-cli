"""CLI commands for friction management."""
from __future__ import annotations

import os
import click

from envoy_cli.friction import (
    FrictionError,
    VALID_LEVELS,
    set_friction,
    get_friction,
    remove_friction,
    list_friction,
)

_DEFAULT_BASE = os.path.expanduser("~/.envoy")


@click.group("friction")
def friction_group() -> None:
    """Track and query env operation friction levels."""


@friction_group.command("set")
@click.argument("name")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--reason", default="", help="Optional reason for this friction level.")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(name: str, level: str, reason: str, base_dir: str) -> None:
    """Set the friction level for NAME."""
    try:
        set_friction(base_dir, name, level, reason)
        click.echo(f"friction for '{name}' set to '{level}'")
    except FrictionError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)


@friction_group.command("get")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(name: str, base_dir: str) -> None:
    """Show the friction level for NAME."""
    try:
        rec = get_friction(base_dir, name)
        click.echo(f"{name}: {rec['level']}" + (f" ({rec['reason']})" if rec["reason"] else ""))
    except FrictionError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)


@friction_group.command("remove")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(name: str, base_dir: str) -> None:
    """Remove the friction record for NAME."""
    try:
        remove_friction(base_dir, name)
        click.echo(f"friction record for '{name}' removed")
    except FrictionError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)


@friction_group.command("list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all friction records."""
    records = list_friction(base_dir)
    if not records:
        click.echo("no friction records found")
        return
    for rec in records:
        reason_part = f" ({rec['reason']})" if rec["reason"] else ""
        click.echo(f"{rec['name']}: {rec['level']}{reason_part}")
