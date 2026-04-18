"""CLI commands for group management."""
import os
import click
from envoy_cli.group import (
    GroupError,
    add_to_group,
    remove_from_group,
    list_group,
    list_all_groups,
    delete_group,
)

_base_dir = os.environ.get("ENVOY_STORE_DIR", os.path.expanduser("~/.envoy"))


@click.group("group")
def group_group():
    """Manage env file groups."""


@group_group.command("add")
@click.argument("group")
@click.argument("env_name")
def add_cmd(group, env_name):
    """Add ENV_NAME to GROUP."""
    try:
        add_to_group(_base_dir, group, env_name)
        click.echo(f"Added '{env_name}' to group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_group.command("remove")
@click.argument("group")
@click.argument("env_name")
def remove_cmd(group, env_name):
    """Remove ENV_NAME from GROUP."""
    try:
        remove_from_group(_base_dir, group, env_name)
        click.echo(f"Removed '{env_name}' from group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_group.command("list")
@click.argument("group", required=False)
def list_cmd(group):
    """List members of GROUP, or all groups if omitted."""
    try:
        if group:
            members = list_group(_base_dir, group)
            if members:
                click.echo("\n".join(members))
            else:
                click.echo(f"Group '{group}' is empty.")
        else:
            all_groups = list_all_groups(_base_dir)
            if not all_groups:
                click.echo("No groups defined.")
            else:
                for g, members in all_groups.items():
                    click.echo(f"{g}: {', '.join(members)}")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_group.command("delete")
@click.argument("group")
def delete_cmd(group):
    """Delete GROUP entirely."""
    try:
        delete_group(_base_dir, group)
        click.echo(f"Deleted group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
