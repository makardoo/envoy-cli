"""CLI commands for archiving and restoring env entries."""
from __future__ import annotations

import os
import click

from envoy_cli.archive import (
    archive_env,
    restore_env,
    list_archived,
    delete_archived,
    ArchiveError,
)
from envoy_cli.storage import load_env, save_env, env_file_path

_BASE = os.environ.get("ENVOY_BASE_DIR", str(os.path.expanduser("~")))


@click.group("archive")
def archive_group() -> None:
    """Archive and restore .env entries."""


@archive_group.command("store")
@click.argument("env_name")
@click.option("--passphrase", prompt=True, hide_input=True)
def store_cmd(env_name: str, passphrase: str) -> None:
    """Archive an env (soft-delete it from active storage)."""
    try:
        content = load_env(env_name, passphrase, base_dir=_BASE)
        archive_env(_BASE, env_name, content)
        p = env_file_path(env_name, base_dir=_BASE)
        if p.exists():
            p.unlink()
        click.echo(f"Archived '{env_name}'.")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_group.command("restore")
@click.argument("env_name")
@click.option("--passphrase", prompt=True, hide_input=True)
def restore_cmd(env_name: str, passphrase: str) -> None:
    """Restore an archived env back to active storage."""
    try:
        content = restore_env(_BASE, env_name)
        save_env(env_name, content, passphrase, base_dir=_BASE)
        click.echo(f"Restored '{env_name}'.")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@archive_group.command("list")
def list_cmd() -> None:
    """List all archived envs."""
    names = list_archived(_BASE)
    if not names:
        click.echo("No archived envs.")
    else:
        for name in names:
            click.echo(name)


@archive_group.command("delete")
@click.argument("env_name")
@click.confirmation_option(prompt="Permanently delete archived env?")
def delete_cmd(env_name: str) -> None:
    """Permanently delete an archived env."""
    try:
        delete_archived(_BASE, env_name)
        click.echo(f"Deleted archived '{env_name}'.")
    except ArchiveError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
