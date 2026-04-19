"""CLI commands for managing event subscriptions."""
import os
import click
from envoy_cli.event import (
    subscribe, unsubscribe, get_subscribers,
    list_all_subscriptions, EventError, VALID_EVENTS,
)

_BASE = os.environ.get("ENVOY_HOME", os.path.expanduser("~/.envoy"))


@click.group("event")
def event_group():
    """Manage event subscriptions."""


@event_group.command("subscribe")
@click.argument("event")
@click.argument("handler")
@click.option("--base-dir", default=_BASE, hidden=True)
def subscribe_cmd(event, handler, base_dir):
    """Subscribe HANDLER command to EVENT."""
    try:
        subscribe(base_dir, event, handler)
        click.echo(f"Subscribed '{handler}' to event '{event}'.")
    except EventError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@event_group.command("unsubscribe")
@click.argument("event")
@click.argument("handler")
@click.option("--base-dir", default=_BASE, hidden=True)
def unsubscribe_cmd(event, handler, base_dir):
    """Unsubscribe HANDLER from EVENT."""
    try:
        unsubscribe(base_dir, event, handler)
        click.echo(f"Unsubscribed '{handler}' from event '{event}'.")
    except EventError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@event_group.command("list")
@click.option("--event", default=None, help="Filter by event name.")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(event, base_dir):
    """List all event subscriptions."""
    if event:
        subs = {event: get_subscribers(base_dir, event)}
    else:
        subs = list_all_subscriptions(base_dir)
    if not any(subs.values()):
        click.echo("No subscriptions found.")
        return
    for ev, handlers in sorted(subs.items()):
        for h in handlers:
            click.echo(f"{ev}: {h}")


@event_group.command("events")
def list_events():
    """List valid event names."""
    for e in sorted(VALID_EVENTS):
        click.echo(e)
