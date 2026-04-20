"""CLI commands for managing env scopes."""

from __future__ import annotations

import os
import sys

import click

from envoy_cli.scope import (
    VALID_SCOPES,
    ScopeError,
    get_scope,
    list_all_scopes,
    list_by_scope,
    remove_scope,
    set_scope,
)

_BASE_DIR = os.environ.get("ENVOY_STORE_DIR", os.path.expanduser("~/.envoy"))


@click.group(name="scope")
def scope_group() -> None:
    """Manage deployment scopes for env files."""


@scope_group.command(name="set")
@click.argument("env_name")
@click.argument("scope", type=click.Choice(sorted(VALID_SCOPES)))
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def set_cmd(env_name: str, scope: str, base_dir: str) -> None:
    """Assign SCOPE to ENV_NAME."""
    try:
        set_scope(base_dir, env_name, scope)
        click.echo(f"Scope for '{env_name}' set to '{scope}'.")
    except ScopeError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@scope_group.command(name="get")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def get_cmd(env_name: str, base_dir: str) -> None:
    """Show the scope assigned to ENV_NAME."""
    try:
        scope = get_scope(base_dir, env_name)
        click.echo(scope)
    except ScopeError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@scope_group.command(name="remove")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def remove_cmd(env_name: str, base_dir: str) -> None:
    """Remove the scope assignment for ENV_NAME."""
    try:
        remove_scope(base_dir, env_name)
        click.echo(f"Scope for '{env_name}' removed.")
    except ScopeError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@scope_group.command(name="list")
@click.option("--scope", default=None, help="Filter by scope.")
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def list_cmd(scope: str | None, base_dir: str) -> None:
    """List env names and their scopes."""
    try:
        if scope:
            names = list_by_scope(base_dir, scope)
            if not names:
                click.echo(f"No envs assigned to scope '{scope}'.")
            else:
                for name in names:
                    click.echo(name)
        else:
            data = list_all_scopes(base_dir)
            if not data:
                click.echo("No scopes defined.")
            else:
                for name, s in sorted(data.items()):
                    click.echo(f"{name}: {s}")
    except ScopeError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
