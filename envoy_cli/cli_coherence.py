"""CLI commands for coherence scoring."""

from __future__ import annotations

import os
import click

from envoy_cli.coherence import (
    CoherenceError,
    compute_coherence,
    get_coherence,
    list_coherence,
)
from envoy_cli.storage import get_env_dir, load_env
from envoy_cli.crypto import decrypt

_DEFAULT_BASE = os.path.join(os.path.expanduser("~"), ".envoy")


@click.group(name="coherence")
def coherence_group() -> None:
    """Analyse env-file coherence (naming conventions, prefix consistency)."""


@coherence_group.command("scan")
@click.argument("env_name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase.")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def scan_cmd(env_name: str, passphrase: str, base_dir: str) -> None:
    """Compute coherence score for ENV_NAME."""
    try:
        raw = load_env(env_name, base_dir=base_dir)
        content = decrypt(raw, passphrase)
        report = compute_coherence(env_name, content, base_dir)
        click.echo(report.summary())
        if report.issues:
            for issue in report.issues:
                click.echo(f"  - {issue}")
    except CoherenceError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)


@coherence_group.command("show")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def show_cmd(env_name: str, base_dir: str) -> None:
    """Show the last recorded coherence report for ENV_NAME."""
    try:
        report = get_coherence(env_name, base_dir)
        click.echo(report.summary())
        if report.issues:
            for issue in report.issues:
                click.echo(f"  - {issue}")
    except CoherenceError as exc:
        click.echo(f"error: {exc}", err=True)
        raise SystemExit(1)


@coherence_group.command("list")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(base_dir: str) -> None:
    """List coherence scores for all recorded environments."""
    reports = list_coherence(base_dir)
    if not reports:
        click.echo("no coherence records found.")
        return
    for r in sorted(reports, key=lambda x: x.score):
        click.echo(r.summary())
