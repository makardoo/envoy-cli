"""CLI commands for env change history."""
from __future__ import annotations
import os
import click
from envoy_cli.history import record_change, get_history, clear_history, HistoryError


@click.group(name="history")
def history_group():
    """View and manage env change history."""


@history_group.command("show")
@click.argument("env_name")
@click.option("--limit", "-n", default=20, show_default=True, help="Max entries to show.")
@click.option("--base-dir", default=None, hidden=True)
def show_history(env_name: str, limit: int, base_dir: str):
    """Show change history for an env."""
    base = base_dir or os.getcwd()
    entries = get_history(base, env_name, limit=limit)
    if not entries:
        click.echo(f"No history found for '{env_name}'.")
        return
    for e in entries:
        import datetime
        ts = datetime.datetime.fromtimestamp(e["ts"]).strftime("%Y-%m-%d %H:%M:%S")
        note = f"  # {e['note']}" if e.get("note") else ""
        click.echo(f"[{ts}] {e['action']} by {e['actor']}{note}")


@history_group.command("clear")
@click.argument("env_name")
@click.option("--base-dir", default=None, hidden=True)
def clear_cmd(env_name: str, base_dir: str):
    """Clear all history for an env."""
    base = base_dir or os.getcwd()
    removed = clear_history(base, env_name)
    click.echo(f"Cleared {removed} history entries for '{env_name}'.")


@history_group.command("record")
@click.argument("env_name")
@click.argument("action")
@click.option("--actor", default="local", show_default=True)
@click.option("--note", default="")
@click.option("--base-dir", default=None, hidden=True)
def record_cmd(env_name: str, action: str, actor: str, note: str, base_dir: str):
    """Manually record a history entry."""
    base = base_dir or os.getcwd()
    try:
        record_change(base, env_name, action, actor=actor, note=note)
        click.echo(f"Recorded '{action}' for '{env_name}'.")
    except HistoryError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
