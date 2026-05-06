"""CLI commands for risk level management."""

from __future__ import annotations

import os
import click

from envoy_cli.risk import (
    RiskError,
    VALID_LEVELS,
    set_risk,
    get_risk,
    remove_risk,
    list_risks,
)

_DEFAULT_BASE = os.path.join(os.path.expanduser("~"), ".envoy")


@click.group(name="risk")
def risk_group():
    """Manage risk levels for env files."""


@risk_group.command(name="set")
@click.argument("name")
@click.argument("level", type=click.Choice(VALID_LEVELS))
@click.option("--note", default="", help="Optional risk note.")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(name: str, level: str, note: str, base_dir: str) -> None:
    """Set risk level for NAME."""
    try:
        set_risk(base_dir, name, level, note)
        click.echo(f"Risk for '{name}' set to '{level}'.")
    except RiskError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@risk_group.command(name="get")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(name: str, base_dir: str) -> None:
    """Show risk level for NAME."""
    info = get_risk(base_dir, name)
    click.echo(f"level: {info['level']}")
    if info.get("note"):
        click.echo(f"note:  {info['note']}")


@risk_group.command(name="remove")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(name: str, base_dir: str) -> None:
    """Remove risk record for NAME."""
    try:
        remove_risk(base_dir, name)
        click.echo(f"Risk record for '{name}' removed.")
    except RiskError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@risk_group.command(name="list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all risk records."""
    records = list_risks(base_dir)
    if not records:
        click.echo("No risk records found.")
        return
    for env_name, info in sorted(records.items()):
        note_part = f"  # {info['note']}" if info.get("note") else ""
        click.echo(f"{env_name}: {info['level']}{note_part}")
