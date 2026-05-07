"""CLI commands for managing env signals."""
from __future__ import annotations

import os
import click

from envoy_cli.signal import (
    SignalError,
    VALID_SIGNALS,
    set_signal,
    get_signal,
    remove_signal,
    list_signals,
)

_DEFAULT_BASE = os.path.expanduser("~/.envoy")


@click.group("signal")
def signal_group() -> None:
    """Manage signals attached to env entries."""


@signal_group.command("set")
@click.argument("env_name")
@click.argument("level", type=click.Choice(sorted(VALID_SIGNALS)))
@click.option("--message", "-m", default="", help="Optional message describing the signal.")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(env_name: str, level: str, message: str, base_dir: str) -> None:
    """Set a signal level for ENV_NAME."""
    try:
        set_signal(base_dir, env_name, level, message)
        click.echo(f"Signal '{level}' set for '{env_name}'.")
    except SignalError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@signal_group.command("get")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(env_name: str, base_dir: str) -> None:
    """Get the signal for ENV_NAME."""
    try:
        info = get_signal(base_dir, env_name)
        click.echo(f"{env_name}: [{info['level']}] {info['message']}")
    except SignalError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@signal_group.command("remove")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(env_name: str, base_dir: str) -> None:
    """Remove the signal for ENV_NAME."""
    try:
        remove_signal(base_dir, env_name)
        click.echo(f"Signal removed for '{env_name}'.")
    except SignalError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@signal_group.command("list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all signals."""
    data = list_signals(base_dir)
    if not data:
        click.echo("No signals recorded.")
        return
    for name, info in sorted(data.items()):
        msg = f" — {info['message']}" if info.get("message") else ""
        click.echo(f"{name}: [{info['level']}]{msg}")
