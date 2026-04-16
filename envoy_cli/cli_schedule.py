"""CLI commands for managing sync schedules."""
import os
import click
from envoy_cli.schedule import (
    ScheduleError, SyncSchedule, add_schedule, remove_schedule,
    list_schedules, toggle_schedule,
)


def _base_dir() -> str:
    return os.environ.get("ENVOY_STORE_DIR", os.path.expanduser("~/.envoy"))


@click.group("schedule")
def schedule_group():
    """Manage scheduled sync jobs."""


@schedule_group.command("add")
@click.argument("env_name")
@click.option("--cron", required=True, help="Cron expression, e.g. '0 * * * *'")
@click.option("--direction", type=click.Choice(["push", "pull"]), default="push", show_default=True)
@click.option("--profile", default="default", show_default=True)
def add(env_name, cron, direction, profile):
    """Add a sync schedule for an environment."""
    try:
        add_schedule(_base_dir(), SyncSchedule(env_name=env_name, cron=cron, direction=direction, profile=profile))
        click.echo(f"Schedule added for '{env_name}' ({direction}) with cron '{cron}'.")
    except ScheduleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schedule_group.command("remove")
@click.argument("env_name")
@click.option("--direction", type=click.Choice(["push", "pull"]), default="push", show_default=True)
def remove(env_name, direction):
    """Remove a sync schedule."""
    try:
        remove_schedule(_base_dir(), env_name, direction)
        click.echo(f"Schedule removed for '{env_name}' ({direction}).")
    except ScheduleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schedule_group.command("list")
def list_all():
    """List all sync schedules."""
    schedules = list_schedules(_base_dir())
    if not schedules:
        click.echo("No schedules configured.")
        return
    for s in schedules:
        status = "enabled" if s.enabled else "disabled"
        click.echo(f"{s.env_name:20s} {s.direction:6s} {s.cron:20s} profile={s.profile} [{status}]")


@schedule_group.command("enable")
@click.argument("env_name")
@click.option("--direction", type=click.Choice(["push", "pull"]), default="push", show_default=True)
def enable(env_name, direction):
    """Enable a sync schedule."""
    try:
        toggle_schedule(_base_dir(), env_name, direction, enabled=True)
        click.echo(f"Schedule for '{env_name}' ({direction}) enabled.")
    except ScheduleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@schedule_group.command("disable")
@click.argument("env_name")
@click.option("--direction", type=click.Choice(["push", "pull"]), default="push", show_default=True)
def disable(env_name, direction):
    """Disable a sync schedule."""
    try:
        toggle_schedule(_base_dir(), env_name, direction, enabled=False)
        click.echo(f"Schedule for '{env_name}' ({direction}) disabled.")
    except ScheduleError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
