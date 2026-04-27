"""CLI commands for managing env endorsements."""
from __future__ import annotations

import click

from envoy_cli.endorsement import (
    EndorsementError,
    add_endorsement,
    get_endorsements,
    list_all_endorsements,
    remove_endorsement,
)

_BASE = click.get_app_dir("envoy")


@click.group(name="endorse")
def endorsement_group() -> None:
    """Manage endorsements for env configs."""


@endorsement_group.command(name="add")
@click.argument("env_name")
@click.argument("endorser")
@click.option("--base-dir", default=_BASE, hidden=True)
def add_cmd(env_name: str, endorser: str, base_dir: str) -> None:
    """Add ENDORSER approval to ENV_NAME."""
    try:
        result = add_endorsement(base_dir, env_name, endorser)
        click.echo(f"Endorsers for '{env_name}': {', '.join(result)}")
    except EndorsementError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@endorsement_group.command(name="remove")
@click.argument("env_name")
@click.argument("endorser")
@click.option("--base-dir", default=_BASE, hidden=True)
def remove_cmd(env_name: str, endorser: str, base_dir: str) -> None:
    """Remove ENDORSER from ENV_NAME."""
    try:
        result = remove_endorsement(base_dir, env_name, endorser)
        remaining = ', '.join(result) if result else '(none)'
        click.echo(f"Remaining endorsers for '{env_name}': {remaining}")
    except EndorsementError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@endorsement_group.command(name="show")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE, hidden=True)
def show_cmd(env_name: str, base_dir: str) -> None:
    """Show endorsers for ENV_NAME."""
    endorsers = get_endorsements(base_dir, env_name)
    if not endorsers:
        click.echo(f"No endorsements for '{env_name}'.")
    else:
        for e in endorsers:
            click.echo(e)


@endorsement_group.command(name="list")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List all endorsements."""
    data = list_all_endorsements(base_dir)
    if not data:
        click.echo("No endorsements recorded.")
        return
    for env_name, endorsers in sorted(data.items()):
        click.echo(f"{env_name}: {', '.join(endorsers)}")
