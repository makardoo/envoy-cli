"""CLI commands for managing env entry expiry dates."""

from __future__ import annotations

import sys
from datetime import datetime, timezone

import click

from envoy_cli.expiry import (
    ExpiryError,
    get_expiry,
    is_expired,
    list_expiries,
    remove_expiry,
    set_expiry,
)
from envoy_cli.storage import get_env_dir

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


@click.group(name="expiry")
def expiry_group():
    """Manage expiry dates for env entries."""


@expiry_group.command("set")
@click.argument("env_name")
@click.argument("expires_at")  # ISO-8601 UTC: 2025-12-31T00:00:00Z
def set_cmd(env_name: str, expires_at: str):
    """Set an expiry date for ENV_NAME (format: 2025-12-31T00:00:00Z)."""
    try:
        dt = datetime.strptime(expires_at, DATE_FMT).replace(tzinfo=timezone.utc)
    except ValueError:
        click.echo(f"Invalid date format. Use {DATE_FMT}", err=True)
        sys.exit(1)
    try:
        set_expiry(get_env_dir(), env_name, dt)
        click.echo(f"Expiry for '{env_name}' set to {expires_at}.")
    except ExpiryError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@expiry_group.command("get")
@click.argument("env_name")
def get_cmd(env_name: str):
    """Show the expiry date for ENV_NAME."""
    try:
        exp = get_expiry(get_env_dir(), env_name)
        status = "EXPIRED" if is_expired(get_env_dir(), env_name) else "active"
        click.echo(f"{env_name}: {exp.strftime(DATE_FMT)} [{status}]")
    except ExpiryError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@expiry_group.command("remove")
@click.argument("env_name")
def remove_cmd(env_name: str):
    """Remove the expiry date for ENV_NAME."""
    try:
        remove_expiry(get_env_dir(), env_name)
        click.echo(f"Expiry for '{env_name}' removed.")
    except ExpiryError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@expiry_group.command("list")
def list_cmd():
    """List all expiry entries."""
    entries = list_expiries(get_env_dir())
    if not entries:
        click.echo("No expiry entries found.")
        return
    now = datetime.now(tz=timezone.utc)
    for name, exp in sorted(entries.items()):
        status = "EXPIRED" if now >= exp else "active"
        click.echo(f"{name}: {exp.strftime(DATE_FMT)} [{status}]")
