"""CLI commands for env metadata management."""
from __future__ import annotations

import os
import click
from envoy_cli.metadata import (
    MetadataError,
    set_metadata,
    get_metadata,
    get_all_metadata,
    remove_metadata,
    list_all_metadata,
)

_BASE = os.environ.get("ENVOY_STORE_DIR", os.path.expanduser("~/.envoy"))


@click.group("metadata")
def metadata_group():
    """Manage arbitrary metadata attached to env names."""


@metadata_group.command("set")
@click.argument("env_name")
@click.argument("key")
@click.argument("value")
def set_cmd(env_name, key, value):
    """Set a metadata key=value for an env."""
    try:
        set_metadata(_BASE, env_name, key, value)
        click.echo(f"Metadata '{key}' set for '{env_name}'.")
    except MetadataError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@metadata_group.command("get")
@click.argument("env_name")
@click.argument("key")
def get_cmd(env_name, key):
    """Get a metadata value for an env."""
    try:
        val = get_metadata(_BASE, env_name, key)
        click.echo(val)
    except MetadataError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@metadata_group.command("remove")
@click.argument("env_name")
@click.argument("key")
def remove_cmd(env_name, key):
    """Remove a metadata key from an env."""
    try:
        remove_metadata(_BASE, env_name, key)
        click.echo(f"Metadata '{key}' removed from '{env_name}'.")
    except MetadataError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@metadata_group.command("show")
@click.argument("env_name")
def show_cmd(env_name):
    """Show all metadata for an env."""
    meta = get_all_metadata(_BASE, env_name)
    if not meta:
        click.echo(f"No metadata for '{env_name}'.")
    else:
        for k, v in meta.items():
            click.echo(f"{k}={v}")


@metadata_group.command("list")
def list_cmd():
    """List all metadata across all envs."""
    all_meta = list_all_metadata(_BASE)
    if not all_meta:
        click.echo("No metadata stored.")
    else:
        for env, pairs in all_meta.items():
            for k, v in pairs.items():
                click.echo(f"{env}  {k}={v}")
