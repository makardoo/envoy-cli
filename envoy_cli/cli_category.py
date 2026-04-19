"""CLI commands for category management."""
import click
from envoy_cli.category import (
    CategoryError,
    set_category,
    get_category,
    remove_category,
    list_by_category,
    list_all_categories,
)

_BASE_DIR = click.get_app_dir("envoy-cli")


@click.group("category")
def category_group():
    """Manage env file categories."""


@category_group.command("set")
@click.argument("env_name")
@click.argument("category")
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def set_cmd(env_name, category, base_dir):
    """Assign a category to an env."""
    try:
        set_category(base_dir, env_name, category)
        click.echo(f"Category '{category}' set for '{env_name}'.")
    except CategoryError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@category_group.command("get")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def get_cmd(env_name, base_dir):
    """Show the category of an env."""
    try:
        cat = get_category(base_dir, env_name)
        click.echo(cat)
    except CategoryError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@category_group.command("remove")
@click.argument("env_name")
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def remove_cmd(env_name, base_dir):
    """Remove the category from an env."""
    try:
        remove_category(base_dir, env_name)
        click.echo(f"Category removed from '{env_name}'.")
    except CategoryError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@category_group.command("list")
@click.option("--filter", "filter_cat", default=None, help="Filter by category name.")
@click.option("--base-dir", default=_BASE_DIR, hidden=True)
def list_cmd(filter_cat, base_dir):
    """List envs and their categories."""
    if filter_cat:
        names = list_by_category(base_dir, filter_cat)
        if not names:
            click.echo(f"No envs in category '{filter_cat}'.")
        for n in names:
            click.echo(n)
    else:
        data = list_all_categories(base_dir)
        if not data:
            click.echo("No categories defined.")
        for name, cat in data.items():
            click.echo(f"{name}: {cat}")
