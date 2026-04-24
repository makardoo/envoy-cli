"""CLI commands for lifecycle state management."""
import os
from pathlib import Path

import click

from .lifecycle import (
    VALID_STATES,
    VALID_TRANSITIONS,
    LifecycleError,
    get_state,
    list_states,
    remove_state,
    set_state,
)


def _base() -> Path:
    return Path(os.environ.get("ENVOY_BASE_DIR", Path.home() / ".envoy_store"))


@click.group(name="lifecycle")
def lifecycle_group():
    """Manage env file lifecycle states."""


@lifecycle_group.command(name="set")
@click.argument("env_name")
@click.argument("state", type=click.Choice(VALID_STATES))
def set_cmd(env_name: str, state: str):
    """Set the lifecycle STATE for ENV_NAME."""
    try:
        result = set_state(_base(), env_name, state)
        click.echo(f"Lifecycle state of '{env_name}' set to '{result}'.")
    except LifecycleError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lifecycle_group.command(name="get")
@click.argument("env_name")
def get_cmd(env_name: str):
    """Get the lifecycle state of ENV_NAME."""
    try:
        state = get_state(_base(), env_name)
        click.echo(state)
    except LifecycleError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lifecycle_group.command(name="remove")
@click.argument("env_name")
def remove_cmd(env_name: str):
    """Remove the lifecycle state for ENV_NAME."""
    try:
        remove_state(_base(), env_name)
        click.echo(f"Lifecycle state for '{env_name}' removed.")
    except LifecycleError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lifecycle_group.command(name="list")
def list_cmd():
    """List all env lifecycle states."""
    states = list_states(_base())
    if not states:
        click.echo("No lifecycle states recorded.")
        return
    for name, state in sorted(states.items()):
        click.echo(f"{name}: {state}")


@lifecycle_group.command(name="transitions")
def transitions_cmd():
    """Show allowed state transitions."""
    for state, targets in VALID_TRANSITIONS.items():
        targets_str = ", ".join(targets) if targets else "(none)"
        click.echo(f"  {state} -> {targets_str}")
