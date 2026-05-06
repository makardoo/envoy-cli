"""CLI commands for managing env clarity levels."""

from __future__ import annotations

import click

from envoy_cli.clarity import (
    ClarityError,
    VALID_LEVELS,
    get_clarity,
    list_clarity,
    remove_clarity,
    set_clarity,
)

_DEFAULT_BASE = ".envoy"


@click.group("clarity")
def clarity_group() -> None:
    """Manage clarity levels for env files."""


@clarity_group.command("set")
@click.argument("env_name")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--note", default="", help="Optional explanatory note.")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(env_name: str, level: str, note: str, base_dir: str) -> None:
    """Set clarity level for ENV_NAME."""
    try:
        set_clarity(base_dir, env_name, level, note)
        click.echo(f"Clarity for '{env_name}' set to '{level}'.")
    except ClarityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@clarity_group.command("get")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(env_name: str, base_dir: str) -> None:
    """Get clarity level for ENV_NAME."""
    try:
        rec = get_clarity(base_dir, env_name)
        click.echo(f"level: {rec['level']}")
        if rec.get("note"):
            click.echo(f"note:  {rec['note']}")
    except ClarityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@clarity_group.command("remove")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(env_name: str, base_dir: str) -> None:
    """Remove clarity record for ENV_NAME."""
    try:
        remove_clarity(base_dir, env_name)
        click.echo(f"Clarity record for '{env_name}' removed.")
    except ClarityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@clarity_group.command("list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all clarity records."""
    data = list_clarity(base_dir)
    if not data:
        click.echo("No clarity records found.")
        return
    for name, rec in sorted(data.items()):
        note_part = f"  # {rec['note']}" if rec.get("note") else ""
        click.echo(f"{name}: {rec['level']}{note_part}")
