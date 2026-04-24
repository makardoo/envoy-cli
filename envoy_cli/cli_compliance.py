"""CLI commands for compliance policy management."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envoy_cli.compliance import (
    ComplianceError,
    check_compliance,
    get_required_keys,
    list_policies,
    remove_policy,
    set_required_keys,
)
from envoy_cli.storage import get_env_dir


@click.group(name="compliance")
def compliance_group():
    """Manage compliance policies for env files."""


@compliance_group.command("set")
@click.argument("env_name")
@click.argument("keys", nargs=-1, required=True)
def set_cmd(env_name: str, keys: tuple):
    """Set required keys policy for ENV_NAME."""
    base = Path(get_env_dir())
    try:
        set_required_keys(base, env_name, list(keys))
        click.echo(f"Policy set for '{env_name}': {', '.join(sorted(keys))}")
    except ComplianceError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@compliance_group.command("get")
@click.argument("env_name")
def get_cmd(env_name: str):
    """Show required keys policy for ENV_NAME."""
    base = Path(get_env_dir())
    try:
        keys = get_required_keys(base, env_name)
        if keys:
            for k in keys:
                click.echo(k)
        else:
            click.echo("(no required keys)")
    except ComplianceError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@compliance_group.command("remove")
@click.argument("env_name")
def remove_cmd(env_name: str):
    """Remove compliance policy for ENV_NAME."""
    base = Path(get_env_dir())
    try:
        remove_policy(base, env_name)
        click.echo(f"Policy removed for '{env_name}'.")
    except ComplianceError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@compliance_group.command("list")
def list_cmd():
    """List all compliance policies."""
    base = Path(get_env_dir())
    policies = list_policies(base)
    if not policies:
        click.echo("No compliance policies defined.")
        return
    for env_name, keys in sorted(policies.items()):
        click.echo(f"{env_name}: {', '.join(keys)}")


@compliance_group.command("check")
@click.argument("env_name")
@click.option("--file", "env_file", required=True, help="Path to .env file to check")
def check_cmd(env_name: str, env_file: str):
    """Check an env file against the compliance policy for ENV_NAME."""
    base = Path(get_env_dir())
    from envoy_cli.diff import parse_env_dict
    try:
        content = Path(env_file).read_text()
    except OSError as exc:
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(1)
    env_dict = parse_env_dict(content)
    result = check_compliance(base, env_name, env_dict)
    if result.passed:
        click.echo(f"✓ '{env_name}' passes compliance checks.")
    else:
        for v in result.violations:
            click.echo(f"✗ {v.reason}")
        sys.exit(1)
