"""CLI commands for badge management."""

import click
from envoy_cli.badge import (
    BadgeError,
    VALID_BADGES,
    set_badge,
    get_badge,
    remove_badge,
    list_badges,
)
from envoy_cli.storage import get_env_dir


@click.group("badge")
def badge_group():
    """Manage status badges for env files."""


@badge_group.command("set")
@click.argument("env_name")
@click.argument("badge", type=click.Choice(sorted(VALID_BADGES)))
def set_cmd(env_name: str, badge: str):
    """Assign a badge to an env."""
    try:
        set_badge(get_env_dir(), env_name, badge)
        click.echo(f"Badge '{badge}' set for '{env_name}'.")
    except BadgeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@badge_group.command("get")
@click.argument("env_name")
def get_cmd(env_name: str):
    """Show the badge for an env."""
    try:
        badge = get_badge(get_env_dir(), env_name)
        click.echo(badge)
    except BadgeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@badge_group.command("remove")
@click.argument("env_name")
def remove_cmd(env_name: str):
    """Remove the badge from an env."""
    try:
        remove_badge(get_env_dir(), env_name)
        click.echo(f"Badge removed from '{env_name}'.")
    except BadgeError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@badge_group.command("list")
def list_cmd():
    """List all env badges."""
    badges = list_badges(get_env_dir())
    if not badges:
        click.echo("No badges set.")
    else:
        for name, badge in sorted(badges.items()):
            click.echo(f"{name}: {badge}")
