"""CLI commands for managing environment type classifications."""
import sys
import click

from envoy_cli.environment_type import (
    EnvironmentTypeError,
    VALID_TYPES,
    set_env_type,
    get_env_type,
    remove_env_type,
    list_env_types,
)
from envoy_cli.storage import get_env_dir


@click.group(name="env-type", help="Manage environment type classifications.")
def env_type_group() -> None:
    pass


@env_type_group.command(name="set")
@click.argument("env_name")
@click.argument("env_type", type=click.Choice(sorted(VALID_TYPES), case_sensitive=False))
def set_cmd(env_name: str, env_type: str) -> None:
    """Assign ENV_TYPE to ENV_NAME."""
    base = get_env_dir()
    try:
        set_env_type(base, env_name, env_type.lower())
        click.echo(f"Set type of '{env_name}' to '{env_type.lower()}'.")
    except EnvironmentTypeError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@env_type_group.command(name="get")
@click.argument("env_name")
def get_cmd(env_name: str) -> None:
    """Show the type assigned to ENV_NAME."""
    base = get_env_dir()
    try:
        t = get_env_type(base, env_name)
        click.echo(t)
    except EnvironmentTypeError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@env_type_group.command(name="remove")
@click.argument("env_name")
def remove_cmd(env_name: str) -> None:
    """Remove the type assignment for ENV_NAME."""
    base = get_env_dir()
    try:
        remove_env_type(base, env_name)
        click.echo(f"Removed type for '{env_name}'.")
    except EnvironmentTypeError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@env_type_group.command(name="list")
def list_cmd() -> None:
    """List all env-type assignments."""
    base = get_env_dir()
    mappings = list_env_types(base)
    if not mappings:
        click.echo("No env-type assignments found.")
        return
    for name, t in sorted(mappings.items()):
        click.echo(f"{name}: {t}")
