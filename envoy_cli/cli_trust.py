"""CLI commands for trust level management."""
from __future__ import annotations

import os

import click

from .trust import (
    TRUST_LEVELS,
    TrustError,
    get_trust,
    list_trust,
    remove_trust,
    set_trust,
)

_base = os.environ.get("ENVOY_STORE_DIR", os.path.expanduser("~/.envoy"))


@click.group("trust")
def trust_group() -> None:
    """Manage trust levels for env files."""


@trust_group.command("set")
@click.argument("name")
@click.argument("level", type=click.Choice(list(TRUST_LEVELS)))
@click.option("--dir", "base_dir", default=_base, hidden=True)
def set_cmd(name: str, level: str, base_dir: str) -> None:
    """Set the trust LEVEL for env NAME."""
    try:
        set_trust(base_dir, name, level)
        click.echo(f"Trust for '{name}' set to '{level}'.")
    except TrustError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trust_group.command("get")
@click.argument("name")
@click.option("--dir", "base_dir", default=_base, hidden=True)
def get_cmd(name: str, base_dir: str) -> None:
    """Get the trust level for env NAME."""
    try:
        level = get_trust(base_dir, name)
        click.echo(level)
    except TrustError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trust_group.command("remove")
@click.argument("name")
@click.option("--dir", "base_dir", default=_base, hidden=True)
def remove_cmd(name: str, base_dir: str) -> None:
    """Remove the trust record for env NAME."""
    try:
        remove_trust(base_dir, name)
        click.echo(f"Trust record for '{name}' removed.")
    except TrustError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@trust_group.command("list")
@click.option("--dir", "base_dir", default=_base, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all trust assignments."""
    entries = list_trust(base_dir)
    if not entries:
        click.echo("No trust records found.")
        return
    for entry in entries:
        click.echo(f"{entry['name']}: {entry['level']}")
