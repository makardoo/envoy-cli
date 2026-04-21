"""CLI commands for ownership management."""
from __future__ import annotations

from pathlib import Path

import click

from .ownership import OwnershipError, get_owner, list_owned, remove_owner, set_owner

_BASE_DIR = Path.home() / ".envoy"


@click.group(name="owner")
def ownership_group() -> None:
    """Manage env file ownership."""


@ownership_group.command("set")
@click.argument("env_name")
@click.argument("owner")
@click.option("--team", default=None, help="Team responsible for this env.")
def set_cmd(env_name: str, owner: str, team: str) -> None:
    """Assign OWNER to ENV_NAME."""
    try:
        set_owner(_BASE_DIR, env_name, owner, team)
        msg = f"Owner of '{env_name}' set to '{owner}'"
        if team:
            msg += f" (team: {team})"
        click.echo(msg)
    except OwnershipError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ownership_group.command("get")
@click.argument("env_name")
def get_cmd(env_name: str) -> None:
    """Show ownership info for ENV_NAME."""
    try:
        info = get_owner(_BASE_DIR, env_name)
        click.echo(f"owner: {info['owner']}")
        if info.get("team"):
            click.echo(f"team:  {info['team']}")
    except OwnershipError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ownership_group.command("remove")
@click.argument("env_name")
def remove_cmd(env_name: str) -> None:
    """Remove ownership record for ENV_NAME."""
    try:
        remove_owner(_BASE_DIR, env_name)
        click.echo(f"Ownership record for '{env_name}' removed.")
    except OwnershipError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ownership_group.command("list")
@click.option("--owner", default=None, help="Filter by owner name.")
@click.option("--team", default=None, help="Filter by team name.")
def list_cmd(owner: str, team: str) -> None:
    """List envs with ownership records."""
    envs = list_owned(_BASE_DIR, owner=owner, team=team)
    if not envs:
        click.echo("No ownership records found.")
    else:
        for name in envs:
            click.echo(name)
