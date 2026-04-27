"""CLI commands for anomaly detection."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envoy_cli.anomaly import scan_env, AnomalyError
from envoy_cli.storage import list_envs


@click.group(name="anomaly", help="Detect anomalies in .env files.")
def anomaly_group() -> None:
    pass


@anomaly_group.command("scan")
@click.argument("env_name")
@click.option("--passphrase", envvar="ENVOY_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--base-dir", default=None, type=click.Path(), help="Override storage base directory.")
def scan_cmd(env_name: str, passphrase: str, base_dir: str | None) -> None:
    """Scan ENV_NAME for anomalies."""
    bd = Path(base_dir) if base_dir else None
    try:
        report = scan_env(env_name, passphrase, base_dir=bd)
    except AnomalyError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(report.summary())
    if not report.clean:
        sys.exit(2)


@anomaly_group.command("scan-all")
@click.option("--passphrase", envvar="ENVOY_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--base-dir", default=None, type=click.Path(), help="Override storage base directory.")
def scan_all_cmd(passphrase: str, base_dir: str | None) -> None:
    """Scan all stored envs for anomalies."""
    bd = Path(base_dir) if base_dir else None
    try:
        names = list_envs(base_dir=bd)
    except Exception as exc:
        click.echo(f"Error listing envs: {exc}", err=True)
        sys.exit(1)
    if not names:
        click.echo("No environments found.")
        return
    found_issues = False
    for name in sorted(names):
        try:
            report = scan_env(name, passphrase, base_dir=bd)
        except AnomalyError as exc:
            click.echo(f"  {name}: skipped ({exc})")
            continue
        click.echo(report.summary())
        if not report.clean:
            found_issues = True
    if found_issues:
        sys.exit(2)
