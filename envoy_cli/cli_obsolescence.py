"""CLI commands for managing env obsolescence."""
from __future__ import annotations

import os

import click

from envoy_cli.obsolescence import (
    ObsolescenceError,
    get_obsolescence,
    list_obsolete,
    mark_obsolete,
    unmark_obsolete,
)

_DEFAULT_BASE = os.path.join(os.path.expanduser("~"), ".envoy")


@click.group(name="obsolescence")
def obsolescence_group() -> None:
    """Manage obsolescence status of env files."""


@obsolescence_group.command("mark")
@click.argument("name")
@click.option("--reason", default="", help="Optional reason for marking obsolete.")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def mark_cmd(name: str, reason: str, base_dir: str) -> None:
    """Mark NAME as obsolete."""
    try:
        entry = mark_obsolete(base_dir, name, reason)
        click.echo(f"Marked '{name}' as obsolete at {entry['marked_at']}.")
    except ObsolescenceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@obsolescence_group.command("unmark")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def unmark_cmd(name: str, base_dir: str) -> None:
    """Remove the obsolescence mark from NAME."""
    try:
        unmark_obsolete(base_dir, name)
        click.echo(f"Removed obsolescence mark from '{name}'.")
    except ObsolescenceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@obsolescence_group.command("get")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(name: str, base_dir: str) -> None:
    """Show the obsolescence record for NAME."""
    try:
        entry = get_obsolescence(base_dir, name)
        click.echo(f"obsolete : {entry['obsolete']}")
        click.echo(f"reason   : {entry['reason'] or '(none)'}")
        click.echo(f"marked_at: {entry['marked_at']}")
    except ObsolescenceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@obsolescence_group.command("list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all envs marked as obsolete."""
    names = list_obsolete(base_dir)
    if not names:
        click.echo("No envs are marked as obsolete.")
    else:
        for n in names:
            click.echo(n)
