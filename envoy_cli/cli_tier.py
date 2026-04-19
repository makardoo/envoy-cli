"""CLI commands for tier management."""
import click
from envoy_cli.tier import (
    set_tier, get_tier, remove_tier, list_tiers,
    TierError, VALID_TIERS,
)

_BASE = click.get_app_dir("envoy")


@click.group("tier")
def tier_group():
    """Manage environment tiers."""


@tier_group.command("set")
@click.argument("env_name")
@click.argument("tier", type=click.Choice(sorted(VALID_TIERS)))
@click.option("--base-dir", default=_BASE, hidden=True)
def set_cmd(env_name, tier, base_dir):
    """Assign a tier to an environment."""
    try:
        set_tier(base_dir, env_name, tier)
        click.echo(f"Tier '{tier}' set for '{env_name}'.")
    except TierError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tier_group.command("get")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE, hidden=True)
def get_cmd(env_name, base_dir):
    """Show the tier for an environment."""
    try:
        tier = get_tier(base_dir, env_name)
        click.echo(tier)
    except TierError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tier_group.command("remove")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE, hidden=True)
def remove_cmd(env_name, base_dir):
    """Remove tier assignment from an environment."""
    try:
        remove_tier(base_dir, env_name)
        click.echo(f"Tier removed for '{env_name}'.")
    except TierError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tier_group.command("list")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(base_dir):
    """List all tier assignments."""
    data = list_tiers(base_dir)
    if not data:
        click.echo("No tiers assigned.")
        return
    for name, tier in sorted(data.items()):
        click.echo(f"{name}: {tier}")
