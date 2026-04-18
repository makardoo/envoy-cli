"""CLI commands for webhook management."""
import os
import click
from envoy_cli.webhook import register_webhook, remove_webhook, list_webhooks, WebhookError

_BASE = os.environ.get("ENVOY_DIR", os.path.expanduser("~/.envoy"))


@click.group("webhook")
def webhook_group():
    """Manage webhook notifications."""


@webhook_group.command("add")
@click.argument("url")
@click.option("--event", "events", multiple=True, help="Event name(s) to subscribe to.")
@click.option("--label", default="", help="Optional label.")
def add_webhook(url: str, events, label: str):
    """Register a new webhook URL."""
    try:
        wh = register_webhook(_BASE, url, list(events), label)
        click.echo(f"Registered webhook: {wh.url}")
    except WebhookError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@webhook_group.command("remove")
@click.argument("url")
def remove_cmd(url: str):
    """Unregister a webhook URL."""
    try:
        remove_webhook(_BASE, url)
        click.echo(f"Removed webhook: {url}")
    except WebhookError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@webhook_group.command("list")
def list_cmd():
    """List all registered webhooks."""
    hooks = list_webhooks(_BASE)
    if not hooks:
        click.echo("No webhooks registered.")
        return
    for wh in hooks:
        events_str = ", ".join(wh.events) if wh.events else "*"
        label_str = f" [{wh.label}]" if wh.label else ""
        click.echo(f"{wh.url}{label_str}  events={events_str}")
