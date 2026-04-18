"""CLI commands for namespace management."""
from __future__ import annotations

import os
import click
from envoy_cli.namespace import (
    NamespaceError,
    assign_namespace,
    get_namespace,
    remove_namespace,
    list_by_namespace,
    list_all_namespaces,
)

_BASE = os.environ.get("ENVOY_STORE_DIR", os.path.expanduser("~/.envoy"))


@click.group(name="namespace")
def namespace_group():
    """Manage env namespaces."""


@namespace_group.command("assign")
@click.argument("env_name")
@click.argument("namespace")
@click.option("--base-dir", default=_BASE, hidden=True)
def assign_cmd(env_name: str, namespace: str, base_dir: str):
    """Assign ENV_NAME to NAMESPACE."""
    try:
        assign_namespace(base_dir, env_name, namespace)
        click.echo(f"Assigned '{env_name}' to namespace '{namespace}'.")
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_group.command("show")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE, hidden=True)
def show_cmd(env_name: str, base_dir: str):
    """Show the namespace for ENV_NAME."""
    try:
        ns = get_namespace(base_dir, env_name)
        click.echo(ns)
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_group.command("remove")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE, hidden=True)
def remove_cmd(env_name: str, base_dir: str):
    """Remove namespace assignment for ENV_NAME."""
    try:
        remove_namespace(base_dir, env_name)
        click.echo(f"Removed namespace for '{env_name}'.")
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_group.command("list")
@click.option("--namespace", default=None, help="Filter by namespace.")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(namespace: str | None, base_dir: str):
    """List envs grouped by namespace."""
    if namespace:
        envs = list_by_namespace(base_dir, namespace)
        if not envs:
            click.echo(f"No envs in namespace '{namespace}'.")
        else:
            for e in envs:
                click.echo(e)
    else:
        mapping = list_all_namespaces(base_dir)
        if not mapping:
            click.echo("No namespaces defined.")
        else:
            for ns, envs in sorted(mapping.items()):
                click.echo(f"{ns}: {', '.join(envs)}")
