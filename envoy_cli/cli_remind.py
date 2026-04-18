"""CLI commands for managing env reminders."""
import os
import click
from envoy_cli.remind import (
    set_reminder, get_reminder, dismiss_reminder,
    due_reminders, list_reminders, ReminderError
)

_base_dir = os.environ.get("ENVOY_BASE_DIR", os.path.expanduser("~/.envoy"))


@click.group(name="remind")
def remind_group():
    """Manage reminders for env files."""


@remind_group.command("set")
@click.argument("env_name")
@click.argument("remind_at")
@click.option("--message", "-m", default="", help="Reminder message")
def set_cmd(env_name, remind_at, message):
    """Set a reminder for ENV_NAME at REMIND_AT (ISO-8601)."""
    try:
        entry = set_reminder(_base_dir, env_name, message, remind_at)
        click.echo(f"Reminder set for '{env_name}' at {entry['remind_at']}")
    except ReminderError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@remind_group.command("show")
@click.argument("env_name")
def show_cmd(env_name):
    """Show reminder for ENV_NAME."""
    try:
        entry = get_reminder(_base_dir, env_name)
        status = "dismissed" if entry["dismissed"] else "active"
        click.echo(f"[{status}] {env_name}: {entry['message']} (due {entry['remind_at']})")
    except ReminderError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@remind_group.command("dismiss")
@click.argument("env_name")
def dismiss_cmd(env_name):
    """Dismiss reminder for ENV_NAME."""
    try:
        dismiss_reminder(_base_dir, env_name)
        click.echo(f"Reminder for '{env_name}' dismissed.")
    except ReminderError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@remind_group.command("due")
def due_cmd():
    """List all due (non-dismissed) reminders."""
    items = due_reminders(_base_dir)
    if not items:
        click.echo("No due reminders.")
        return
    for item in items:
        click.echo(f"  {item['env_name']}: {item['message']} (due {item['remind_at']})")


@remind_group.command("list")
def list_cmd():
    """List all reminders."""
    items = list_reminders(_base_dir)
    if not items:
        click.echo("No reminders set.")
        return
    for item in items:
        status = "dismissed" if item["dismissed"] else "active"
        click.echo(f"  [{status}] {item['env_name']}: {item['message']} (due {item['remind_at']})")
