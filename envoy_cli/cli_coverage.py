"""CLI commands for env key coverage reporting."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envoy_cli.coverage import (
    CoverageError,
    compute_coverage,
    get_coverage,
    list_coverage,
)
from envoy_cli.storage import load_env

_DEFAULT_BASE = Path.home() / ".envoy"


@click.group(name="coverage")
def coverage_group() -> None:
    """Track key coverage for .env files."""


@coverage_group.command(name="check")
@click.argument("env_name")
@click.option(
    "--require",
    "required_keys",
    multiple=True,
    required=True,
    help="Required key (repeatable).",
)
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--base-dir", default=str(_DEFAULT_BASE), show_default=True)
def check_cmd(
    env_name: str,
    required_keys: tuple,
    passphrase: str,
    base_dir: str,
) -> None:
    """Compute and display coverage for ENV_NAME."""
    base = Path(base_dir)
    try:
        content = load_env(env_name, passphrase, base_dir=base)
        report = compute_coverage(env_name, content, list(required_keys), base)
    except CoverageError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(report.summary)
    if report.missing_keys:
        click.echo("Missing keys:")
        for k in report.missing_keys:
            click.echo(f"  - {k}")
    if report.extra_keys:
        click.echo("Extra keys (not in schema):")
        for k in report.extra_keys:
            click.echo(f"  + {k}")

    if report.score < 1.0:
        sys.exit(2)


@coverage_group.command(name="show")
@click.argument("env_name")
@click.option("--base-dir", default=str(_DEFAULT_BASE), show_default=True)
def show_cmd(env_name: str, base_dir: str) -> None:
    """Show the last computed coverage report for ENV_NAME."""
    base = Path(base_dir)
    try:
        report = get_coverage(env_name, base)
    except CoverageError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    click.echo(report.summary)
    click.echo(f"  Present : {', '.join(report.present_keys) or '(none)'}")
    click.echo(f"  Missing : {', '.join(report.missing_keys) or '(none)'}")
    click.echo(f"  Extra   : {', '.join(report.extra_keys) or '(none)'}")


@coverage_group.command(name="list")
@click.option("--base-dir", default=str(_DEFAULT_BASE), show_default=True)
def list_cmd(base_dir: str) -> None:
    """List all env names with a stored coverage report."""
    base = Path(base_dir)
    names = list_coverage(base)
    if not names:
        click.echo("No coverage reports found.")
    else:
        for name in names:
            click.echo(name)
