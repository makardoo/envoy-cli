"""CLI commands for access control."""
import click
from envoy_cli.access import (
    set_permission, get_permission, list_permissions,
    remove_permission, check_permission, AccessError
)
from envoy_cli.storage import get_env_dir


@click.group("access")
def access_group():
    """Manage per-env access permissions."""


@access_group.command("grant")
@click.argument("env_name")
@click.argument("profile")
@click.option("--no-write", is_flag=True, help="Grant read-only access")
def grant(env_name, profile, no_write):
    """Grant a profile read (and optionally write) access to an env."""
    base = get_env_dir()
    try:
        set_permission(base, env_name, profile, can_read=True, can_write=not no_write)
        mode = "read-only" if no_write else "read/write"
        click.echo(f"Granted {mode} access to '{env_name}' for profile '{profile}'.")
    except AccessError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@access_group.command("revoke")
@click.argument("env_name")
@click.argument("profile")
def revoke(env_name, profile):
    """Remove access entry for a profile on an env."""
    base = get_env_dir()
    try:
        remove_permission(base, env_name, profile)
        click.echo(f"Revoked access to '{env_name}' for profile '{profile}'.")
    except AccessError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@access_group.command("show")
@click.argument("env_name")
def show(env_name):
    """Show all permissions for an env."""
    base = get_env_dir()
    perms = list_permissions(base, env_name)
    if not perms:
        click.echo(f"No explicit permissions set for '{env_name}'.")
        return
    for profile, bits in perms.items():
        r = "r" if bits.get("read", True) else "-"
        w = "w" if bits.get("write", True) else "-"
        click.echo(f"  {profile}: {r}{w}")


@access_group.command("check")
@click.argument("env_name")
@click.argument("profile")
@click.argument("action", type=click.Choice(["read", "write"]))
def check(env_name, profile, action):
    """Check if a profile can perform action on env."""
    base = get_env_dir()
    allowed = check_permission(base, env_name, profile, action)
    status = "allowed" if allowed else "denied"
    click.echo(f"{action} on '{env_name}' for '{profile}': {status}")
    if not allowed:
        raise SystemExit(1)
