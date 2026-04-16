"""CLI commands for env tagging."""
import click
from envoy_cli.storage import get_env_dir
from envoy_cli.tag import TagError, add_tag, get_tag, list_tags, remove_tag


@click.group("tag")
def tag_group():
    """Manage tags for env snapshots."""


@tag_group.command("add")
@click.argument("tag")
@click.argument("env_name")
@click.argument("ref")
@click.option("--base-dir", default=None, help="Override storage base directory.")
def add(tag: str, env_name: str, ref: str, base_dir):
    """Tag an env snapshot ref with a human-readable label."""
    base = base_dir or get_env_dir()
    try:
        add_tag(base, tag, env_name, ref)
        click.echo(f"Tagged '{env_name}' as '{tag}' -> {ref}")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tag_group.command("remove")
@click.argument("tag")
@click.option("--base-dir", default=None)
def remove(tag: str, base_dir):
    """Remove a tag."""
    base = base_dir or get_env_dir()
    try:
        remove_tag(base, tag)
        click.echo(f"Removed tag '{tag}'.")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tag_group.command("show")
@click.argument("tag")
@click.option("--base-dir", default=None)
def show(tag: str, base_dir):
    """Show what a tag points to."""
    base = base_dir or get_env_dir()
    try:
        info = get_tag(base, tag)
        click.echo(f"tag:  {tag}")
        click.echo(f"env:  {info['env']}")
        click.echo(f"ref:  {info['ref']}")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@tag_group.command("list")
@click.option("--base-dir", default=None)
def list_all(base_dir):
    """List all tags."""
    base = base_dir or get_env_dir()
    tags = list_tags(base)
    if not tags:
        click.echo("No tags found.")
        return
    for entry in tags:
        click.echo(f"{entry['tag']:20s}  {entry['env']:20s}  {entry['ref']}")
