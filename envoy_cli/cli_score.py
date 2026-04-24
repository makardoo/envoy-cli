"""CLI commands for environment scoring."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envoy_cli.environment_score import (
    ScoreError,
    compute_score,
    record_score,
    get_score,
    list_scores,
)
from envoy_cli.storage import get_env_dir


_base_dir: Path | None = None  # overridden in tests


def _base() -> Path:
    return _base_dir or get_env_dir()


@click.group("score")
def score_group() -> None:
    """Commands for computing and tracking env quality scores."""


@score_group.command("compute")
@click.argument("env_name")
@click.option("--passphrase", "-p", required=True, help="Decryption passphrase.")
@click.option("--save", "save_result", is_flag=True, default=False, help="Persist the score.")
def compute_cmd(env_name: str, passphrase: str, save_result: bool) -> None:
    """Compute the quality score for ENV_NAME."""
    try:
        s = compute_score(env_name, passphrase, base_dir=_base())
    except ScoreError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(f"{env_name}: {s}/100")
    if save_result:
        record_score(env_name, s, base_dir=_base())
        click.echo("Score saved.")


@score_group.command("show")
@click.argument("env_name")
def show_cmd(env_name: str) -> None:
    """Show the last recorded score for ENV_NAME."""
    try:
        rec = get_score(env_name, base_dir=_base())
    except ScoreError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(f"{rec['env']}: {rec['score']}/100")


@score_group.command("list")
def list_cmd() -> None:
    """List all recorded scores."""
    records = list_scores(base_dir=_base())
    if not records:
        click.echo("No scores recorded.")
        return
    for rec in records:
        click.echo(f"{rec['env']}: {rec['score']}/100")
