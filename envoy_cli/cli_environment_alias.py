"""CLI commands for managing environment aliases."""
from __future__ import annotations

import os
import sys

import click

from .environment_alias import (
    EnvAliasError,
    list_env_aliases,
    remove_env_alias,
    resolve_env_alias,
    set_env_alias,
)

_DEFAULT_BASE = os.path.expanduser("~/.envoy")


@click.group(name="env-alias")
def env_alias_group() -> None:
    """Manage short-name aliases for environment identifiers."""


@env_alias_group.command("set")
@click.argument("alias")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(alias: str, env_name: str, base_dir: str) -> None:
    """Map ALIAS to ENV_NAME."""
    try:
        set_env_alias(base_dir, alias, env_name)
        click.echo(f"Alias '{alias}' -> '{env_name}' saved.")
    except EnvAliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@env_alias_group.command("get")
@click.argument("alias")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(alias: str, base_dir: str) -> None:
    """Resolve ALIAS to its env name."""
    try:
        env_name = resolve_env_alias(base_dir, alias)
        click.echo(env_name)
    except EnvAliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@env_alias_group.command("remove")
@click.argument("alias")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(alias: str, base_dir: str) -> None:
    """Remove an alias mapping."""
    try:
        remove_env_alias(base_dir, alias)
        click.echo(f"Alias '{alias}' removed.")
    except EnvAliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@env_alias_group.command("list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all alias mappings."""
    entries = list_env_aliases(base_dir)
    if not entries:
        click.echo("No aliases defined.")
        return
    for entry in entries:
        click.echo(f"{entry['alias']!s:30s} -> {entry['env_name']}")
