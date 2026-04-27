"""CLI commands for the reputation module."""
from __future__ import annotations

import os
from pathlib import Path

import click

from .reputation import (
    ReputationError,
    REPUTATION_LEVELS,
    _SCORE_WEIGHTS,
    compute_reputation,
    list_reputations,
    record_event,
    reset_reputation,
)


def _base_dir() -> Path:
    return Path(os.environ.get("ENVOY_HOME", Path.home() / ".envoy"))


@click.group("reputation")
def reputation_group() -> None:
    """Manage env-file reputation scores."""


@reputation_group.command("record")
@click.argument("env_name")
@click.argument("event", type=click.Choice(list(_SCORE_WEIGHTS)))
def record_cmd(env_name: str, event: str) -> None:
    """Record a positive reputation EVENT for ENV_NAME."""
    try:
        record_event(_base_dir(), env_name, event)
        click.echo(f"Recorded '{event}' for '{env_name}'.")
    except ReputationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@reputation_group.command("show")
@click.argument("env_name")
def show_cmd(env_name: str) -> None:
    """Show reputation score for ENV_NAME."""
    try:
        rep = compute_reputation(_base_dir(), env_name)
    except ReputationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo(f"Env:   {rep['env_name']}")
    click.echo(f"Score: {rep['score']}")
    click.echo(f"Level: {rep['level']}")
    click.echo("Counters:")
    for k, v in rep["counters"].items():  # type: ignore[union-attr]
        click.echo(f"  {k}: {v}")


@reputation_group.command("list")
def list_cmd() -> None:
    """List reputation scores for all tracked envs."""
    reps = list_reputations(_base_dir())
    if not reps:
        click.echo("No reputation records found.")
        return
    for rep in reps:
        click.echo(f"{rep['env_name']:<20} score={rep['score']:<6} level={rep['level']}")


@reputation_group.command("reset")
@click.argument("env_name")
def reset_cmd(env_name: str) -> None:
    """Reset reputation record for ENV_NAME."""
    try:
        reset_reputation(_base_dir(), env_name)
        click.echo(f"Reputation for '{env_name}' has been reset.")
    except ReputationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
