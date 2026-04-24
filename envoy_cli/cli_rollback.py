"""CLI commands for rolling back env files to previous snapshots."""
from __future__ import annotations

from pathlib import Path

import click

from envoy_cli.rollback import (
    RollbackError,
    list_rollback_points,
    rollback_to_snapshot,
    rollback_to_latest,
)


_base_dir = Path.home() / ".envoy"


@click.group("rollback")
def rollback_group() -> None:
    """Rollback env files to previous snapshots."""


@rollback_group.command("list")
@click.argument("env_name")
@click.option("--base-dir", default=None, hidden=True)
def list_cmd(env_name: str, base_dir: str | None) -> None:
    """List available rollback points (snapshots) for ENV_NAME."""
    base = Path(base_dir) if base_dir else _base_dir
    try:
        points = list_rollback_points(base, env_name)
    except RollbackError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    if not points:
        click.echo(f"No snapshots found for '{env_name}'.")
        return
    for name in points:
        click.echo(name)


@rollback_group.command("to")
@click.argument("env_name")
@click.argument("snapshot_name")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--base-dir", default=None, hidden=True)
def to_cmd(env_name: str, snapshot_name: str, passphrase: str, base_dir: str | None) -> None:
    """Rollback ENV_NAME to SNAPSHOT_NAME."""
    base = Path(base_dir) if base_dir else _base_dir
    try:
        rollback_to_snapshot(base, env_name, snapshot_name, passphrase)
        click.echo(f"Rolled back '{env_name}' to snapshot '{snapshot_name}'.")
    except RollbackError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@rollback_group.command("latest")
@click.argument("env_name")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--base-dir", default=None, hidden=True)
def latest_cmd(env_name: str, passphrase: str, base_dir: str | None) -> None:
    """Rollback ENV_NAME to its most recent snapshot."""
    base = Path(base_dir) if base_dir else _base_dir
    try:
        rollback_to_latest(base, env_name, passphrase)
        click.echo(f"Rolled back '{env_name}' to the latest snapshot.")
    except RollbackError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
