"""CLI commands for managing env severity levels."""
from __future__ import annotations

import os
import sys

import click

from .severity import (
    VALID_LEVELS,
    SeverityError,
    get_severity,
    list_severities,
    remove_severity,
    set_severity,
)

_BASE_DIR = os.environ.get("ENVOY_HOME", os.path.expanduser("~/.envoy"))


@click.group("severity")
def severity_group() -> None:
    """Manage severity levels for env files."""


@severity_group.command("set")
@click.argument("name")
@click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
def set_cmd(name: str, level: str) -> None:
    """Set the severity level for NAME."""
    try:
        set_severity(_BASE_DIR, name, level.lower())
        click.echo(f"severity for {name!r} set to {level.lower()!r}")
    except SeverityError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@severity_group.command("get")
@click.argument("name")
def get_cmd(name: str) -> None:
    """Get the severity level for NAME."""
    try:
        level = get_severity(_BASE_DIR, name)
        click.echo(level)
    except SeverityError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@severity_group.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Remove the severity entry for NAME."""
    try:
        remove_severity(_BASE_DIR, name)
        click.echo(f"severity entry for {name!r} removed")
    except SeverityError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)


@severity_group.command("list")
def list_cmd() -> None:
    """List all severity entries."""
    entries = list_severities(_BASE_DIR)
    if not entries:
        click.echo("no severity entries found")
        return
    for env_name, level in sorted(entries.items()):
        click.echo(f"{env_name}: {level}")
