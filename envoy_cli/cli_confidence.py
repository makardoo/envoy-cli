"""CLI commands for managing env confidence levels."""
import os
import click
from envoy_cli.confidence import (
    ConfidenceError,
    LEVELS,
    set_confidence,
    get_confidence,
    remove_confidence,
    list_confidence,
)

_BASE = os.environ.get("ENVOY_HOME", os.path.expanduser("~/.envoy"))


@click.group("confidence")
def confidence_group():
    """Manage confidence levels for env files."""


@confidence_group.command("set")
@click.argument("name")
@click.argument("level", type=click.Choice(LEVELS))
@click.option("--note", default="", help="Optional note.")
def set_cmd(name: str, level: str, note: str) -> None:
    """Set confidence level for NAME."""
    try:
        set_confidence(_BASE, name, level, note)
        click.echo(f"confidence for '{name}' set to '{level}'")
    except ConfidenceError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@confidence_group.command("get")
@click.argument("name")
def get_cmd(name: str) -> None:
    """Show confidence level for NAME."""
    try:
        rec = get_confidence(_BASE, name)
        click.echo(f"{name}: {rec['level']}" + (f" ({rec['note']})" if rec["note"] else ""))
    except ConfidenceError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@confidence_group.command("remove")
@click.argument("name")
def remove_cmd(name: str) -> None:
    """Remove confidence record for NAME."""
    try:
        remove_confidence(_BASE, name)
        click.echo(f"confidence record for '{name}' removed")
    except ConfidenceError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@confidence_group.command("list")
def list_cmd() -> None:
    """List all confidence records."""
    records = list_confidence(_BASE)
    if not records:
        click.echo("no confidence records found")
        return
    for name, rec in sorted(records.items()):
        note = f" ({rec['note']})" if rec["note"] else ""
        click.echo(f"{name}: {rec['level']}{note}")
