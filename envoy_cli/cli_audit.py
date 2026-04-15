"""CLI commands for viewing the audit log."""

import click
from tabulate import tabulate

from envoy_cli.audit import read_audit_log, filter_audit_log
from envoy_cli.storage import get_env_dir


@click.group("audit")
def audit_group():
    """View audit logs for env operations."""
    pass


@audit_group.command("log")
@click.option("--env", "env_name", default=None, help="Filter by env name.")
@click.option("--action", default=None, help="Filter by action (set, get, push, pull, remove).")
@click.option("--environment", default=None, help="Filter by environment (local, staging, production).")
@click.option("--limit", default=20, show_default=True, help="Maximum number of entries to show.")
def show_log(env_name, action, environment, limit):
    """Display recent audit log entries."""
    env_dir = get_env_dir()
    entries = read_audit_log(env_dir)
    entries = filter_audit_log(entries, env_name=env_name, action=action, environment=environment)
    entries = entries[-limit:]

    if not entries:
        click.echo("No audit log entries found.")
        return

    rows = [
        [
            e.get("timestamp", "")[:19].replace("T", " "),
            e.get("action", ""),
            e.get("env_name", ""),
            e.get("environment", ""),
            e.get("user", ""),
            e.get("details") or "",
        ]
        for e in entries
    ]
    headers = ["Timestamp", "Action", "Env Name", "Environment", "User", "Details"]
    click.echo(tabulate(rows, headers=headers, tablefmt="simple"))


@audit_group.command("clear")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def clear_log():
    """Clear the audit log."""
    import os
    from envoy_cli.audit import get_audit_log_path

    env_dir = get_env_dir()
    log_path = get_audit_log_path(env_dir)
    if log_path.exists():
        os.remove(log_path)
        click.echo("Audit log cleared.")
    else:
        click.echo("No audit log to clear.")
