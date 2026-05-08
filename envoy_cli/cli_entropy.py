"""CLI commands for entropy analysis of .env files."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envoy_cli.entropy import compute_entropy, EntropyError


@click.group("entropy")
def entropy_group() -> None:
    """Analyse value entropy in stored environments."""


@entropy_group.command("scan")
@click.argument("env_name")
@click.option("--passphrase", "-p", prompt=True, hide_input=True, help="Decryption passphrase.")
@click.option("--base-dir", default=None, type=click.Path(), help="Override storage base directory.")
@click.option("--threshold", "-t", default=3.5, show_default=True, type=float,
              help="Entropy threshold for HIGH classification.")
def scan_cmd(env_name: str, passphrase: str, base_dir: str | None, threshold: float) -> None:
    """Print per-key entropy scores for ENV_NAME."""
    base = Path(base_dir) if base_dir else None
    try:
        report = compute_entropy(env_name, passphrase, base_dir=base)
    except EntropyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    # Allow caller to override threshold at display time.
    report.HIGH_THRESHOLD = threshold
    report.high_entropy_keys = [k for k, v in report.scores.items() if v >= threshold]

    click.echo(report.summary())
    if report.high_entropy_keys:
        sys.exit(2)


@entropy_group.command("average")
@click.argument("env_name")
@click.option("--passphrase", "-p", prompt=True, hide_input=True)
@click.option("--base-dir", default=None, type=click.Path())
def average_cmd(env_name: str, passphrase: str, base_dir: str | None) -> None:
    """Print only the average entropy score for ENV_NAME."""
    base = Path(base_dir) if base_dir else None
    try:
        report = compute_entropy(env_name, passphrase, base_dir=base)
    except EntropyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(f"{report.average:.4f}")
