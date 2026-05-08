"""CLI commands for env-file change velocity tracking."""
from __future__ import annotations

import os
from pathlib import Path

import click

from envoy_cli.velocity import (
    VelocityError,
    compute_velocity,
    get_changes,
    record_change,
    clear_changes,
)


def _base_dir() -> Path:
    return Path(os.environ.get("ENVOY_HOME", Path.home() / ".envoy"))


@click.group("velocity")
def velocity_group() -> None:
    """Track rate-of-change velocity for env files."""


@velocity_group.command("record")
@click.argument("env_name")
def record_cmd(env_name: str) -> None:
    """Record a change event for ENV_NAME."""
    try:
        ts = record_change(_base_dir(), env_name)
        click.echo(f"Recorded change for '{env_name}' at {ts}")
    except VelocityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@velocity_group.command("show")
@click.argument("env_name")
def show_cmd(env_name: str) -> None:
    """Show velocity summary for ENV_NAME."""
    try:
        v = compute_velocity(_base_dir(), env_name)
        click.echo(f"env       : {v['env_name']}")
        click.echo(f"total     : {v['total']}")
        click.echo(f"last 24 h : {v['last_24h']}")
        click.echo(f"last change: {v['last_change'] or 'never'}")
    except VelocityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@velocity_group.command("list")
@click.argument("env_name")
def list_cmd(env_name: str) -> None:
    """List all recorded change timestamps for ENV_NAME."""
    try:
        changes = get_changes(_base_dir(), env_name)
        if not changes:
            click.echo("No changes recorded.")
        for ts in changes:
            click.echo(ts)
    except VelocityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@velocity_group.command("clear")
@click.argument("env_name")
def clear_cmd(env_name: str) -> None:
    """Clear all recorded changes for ENV_NAME."""
    try:
        clear_changes(_base_dir(), env_name)
        click.echo(f"Cleared velocity history for '{env_name}'.")
    except VelocityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
