"""CLI commands for the spotlight feature."""

from __future__ import annotations

import os
import click

from envoy_cli.spotlight import (
    SpotlightError,
    spotlight_env,
    remove_spotlight,
    get_spotlight,
    list_spotlights,
)

_DEFAULT_BASE = os.path.expanduser("~/.envoy")


@click.group(name="spotlight")
def spotlight_group() -> None:
    """Manage spotlighted / featured env files."""


@spotlight_group.command(name="add")
@click.argument("name")
@click.option("--reason", default="", help="Why this env is spotlighted.")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def add_cmd(name: str, reason: str, base_dir: str) -> None:
    """Spotlight an env."""
    try:
        spotlight_env(base_dir, name, reason)
        click.echo(f"Spotlighted '{name}'.")
    except SpotlightError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@spotlight_group.command(name="remove")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(name: str, base_dir: str) -> None:
    """Remove spotlight from an env."""
    try:
        remove_spotlight(base_dir, name)
        click.echo(f"Removed spotlight from '{name}'.")
    except SpotlightError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@spotlight_group.command(name="get")
@click.argument("name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(name: str, base_dir: str) -> None:
    """Show the spotlight reason for an env."""
    try:
        reason = get_spotlight(base_dir, name)
        click.echo(reason if reason else "(no reason given)")
    except SpotlightError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@spotlight_group.command(name="list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all spotlighted envs."""
    entries = list_spotlights(base_dir)
    if not entries:
        click.echo("No spotlighted envs.")
        return
    for entry in entries:
        reason = f" — {entry['reason']}" if entry["reason"] else ""
        click.echo(f"{entry['name']}{reason}")
