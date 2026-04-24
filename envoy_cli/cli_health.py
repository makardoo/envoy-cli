"""CLI commands for environment health checks."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envoy_cli.environment_health import (
    HealthError,
    check_health,
    get_health_rules,
    set_health_rule,
)
from envoy_cli.storage import get_env_dir, load_env
from envoy_cli.env_file import decrypt_env

_base_dir = Path.home()


@click.group("health")
def health_group():
    """Health check commands for environments."""


@health_group.command("set-rule")
@click.argument("env_name")
@click.option("--min-keys", type=int, default=None, help="Minimum number of keys required.")
@click.option("--required-keys", default=None, help="Comma-separated list of required keys.")
@click.option("--warn-empty-values", is_flag=True, default=False, help="Warn on empty values.")
@click.option("--base-dir", default=None, hidden=True)
def set_rule(env_name, min_keys, required_keys, warn_empty_values, base_dir):
    """Configure health rules for an environment."""
    base = Path(base_dir) if base_dir else _base_dir
    try:
        if min_keys is not None:
            set_health_rule(base, env_name, "min_keys", min_keys)
        if required_keys is not None:
            keys = [k.strip() for k in required_keys.split(",") if k.strip()]
            set_health_rule(base, env_name, "required_keys", keys)
        if warn_empty_values:
            set_health_rule(base, env_name, "warn_empty_values", True)
        click.echo(f"Health rules updated for '{env_name}'.")
    except HealthError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@health_group.command("show-rules")
@click.argument("env_name")
@click.option("--base-dir", default=None, hidden=True)
def show_rules(env_name, base_dir):
    """Show configured health rules for an environment."""
    base = Path(base_dir) if base_dir else _base_dir
    try:
        rules = get_health_rules(base, env_name)
        if not rules:
            click.echo("No rules configured.")
            return
        for k, v in rules.items():
            click.echo(f"  {k}: {v}")
    except HealthError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@health_group.command("check")
@click.argument("env_name")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option("--base-dir", default=None, hidden=True)
def check_cmd(env_name, passphrase, base_dir):
    """Run health checks against a stored environment."""
    base = Path(base_dir) if base_dir else _base_dir
    try:
        encrypted = load_env(env_name, base_dir=base)
        content = decrypt_env(encrypted, passphrase)
        report = check_health(base, env_name, content)
        click.echo(report.summary)
        for issue in report.issues:
            icon = "✗" if issue.severity == "error" else "⚠" if issue.severity == "warning" else "i"
            click.echo(f"  [{icon}] {issue.code}: {issue.message}")
        if not report.healthy:
            sys.exit(1)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
