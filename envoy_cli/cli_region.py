"""CLI commands for region management."""
import click
from envoy_cli.region import (
    set_region, get_region, remove_region, list_regions,
    RegionError, VALID_REGIONS,
)


@click.group("region")
def region_group():
    """Manage region assignments for env files."""


@region_group.command("set")
@click.argument("env_name")
@click.argument("region")
@click.option("--base-dir", default=".envoy", show_default=True)
def set_cmd(env_name, region, base_dir):
    """Assign a region to an env file."""
    try:
        set_region(base_dir, env_name, region)
        click.echo(f"Region '{region}' assigned to '{env_name}'.")
    except RegionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@region_group.command("get")
@click.argument("env_name")
@click.option("--base-dir", default=".envoy", show_default=True)
def get_cmd(env_name, base_dir):
    """Show region for an env file."""
    try:
        r = get_region(base_dir, env_name)
        click.echo(r)
    except RegionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@region_group.command("remove")
@click.argument("env_name")
@click.option("--base-dir", default=".envoy", show_default=True)
def remove_cmd(env_name, base_dir):
    """Remove region assignment from an env file."""
    try:
        remove_region(base_dir, env_name)
        click.echo(f"Region assignment removed for '{env_name}'.")
    except RegionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@region_group.command("list")
@click.option("--base-dir", default=".envoy", show_default=True)
def list_cmd(base_dir):
    """List all region assignments."""
    data = list_regions(base_dir)
    if not data:
        click.echo("No region assignments found.")
    else:
        for name, region in sorted(data.items()):
            click.echo(f"{name}: {region}")


@region_group.command("list-valid")
def list_valid():
    """List valid region identifiers."""
    for r in sorted(VALID_REGIONS):
        click.echo(r)
