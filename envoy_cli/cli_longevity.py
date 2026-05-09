"""CLI commands for longevity tracking."""

from __future__ import annotations

import os
from pathlib import Path

import click

from envoy_cli.longevity import (
    LongevityError,
    delete_longevity,
    get_longevity,
    list_longevity,
    record_creation,
)

_BASE_DIR = Path(os.environ.get("ENVOY_HOME", Path.home() / ".envoy"))


@click.group(name="longevity")
def longevity_group() -> None:
    """Track how long env files have existed."""


@longevity_group.command("record")
@click.argument("name")
@click.option("--base-dir", default=None, hidden=True)
def record_cmd(name: str, base_dir: str | None) -> None:
    """Record the creation timestamp for NAME (idempotent)."""
    base = Path(base_dir) if base_dir else _BASE_DIR
    try:
        ts = record_creation(base, name)
        click.echo(f"Recorded creation of '{name}' at {ts}")
    except LongevityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@longevity_group.command("show")
@click.argument("name")
@click.option("--base-dir", default=None, hidden=True)
def show_cmd(name: str, base_dir: str | None) -> None:
    """Show longevity info for NAME."""
    base = Path(base_dir) if base_dir else _BASE_DIR
    try:
        info = get_longevity(base, name)
        click.echo(f"name      : {info['name']}")
        click.echo(f"created_at: {info['created_at']}")
        click.echo(f"age_days  : {info['age_days']}")
    except LongevityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@longevity_group.command("remove")
@click.argument("name")
@click.option("--base-dir", default=None, hidden=True)
def remove_cmd(name: str, base_dir: str | None) -> None:
    """Remove the longevity record for NAME."""
    base = Path(base_dir) if base_dir else _BASE_DIR
    try:
        delete_longevity(base, name)
        click.echo(f"Removed longevity record for '{name}'")
    except LongevityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@longevity_group.command("list")
@click.option("--base-dir", default=None, hidden=True)
def list_cmd(base_dir: str | None) -> None:
    """List all tracked envs sorted by age (oldest first)."""
    base = Path(base_dir) if base_dir else _BASE_DIR
    entries = list_longevity(base)
    if not entries:
        click.echo("No longevity records found.")
        return
    for entry in entries:
        click.echo(f"{entry['name']:30s}  created={entry['created_at']}  age={entry['age_days']}d")
