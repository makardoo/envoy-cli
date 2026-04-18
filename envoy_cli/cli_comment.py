"""CLI commands for managing inline key comments."""
import click
from envoy_cli.comment import set_comment, get_comment, remove_comment, list_comments, CommentError
from envoy_cli.storage import get_env_dir


@click.group(name="comment")
def comment_group():
    """Manage inline comments for env keys."""


@comment_group.command("set")
@click.argument("env_name")
@click.argument("key")
@click.argument("comment")
def set_cmd(env_name, key, comment):
    """Attach a comment to a key in an env."""
    try:
        set_comment(get_env_dir(), env_name, key, comment)
        click.echo(f"Comment set for '{key}' in '{env_name}'.")
    except CommentError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@comment_group.command("get")
@click.argument("env_name")
@click.argument("key")
def get_cmd(env_name, key):
    """Show the comment for a key."""
    try:
        c = get_comment(get_env_dir(), env_name, key)
        click.echo(c)
    except CommentError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@comment_group.command("remove")
@click.argument("env_name")
@click.argument("key")
def remove_cmd(env_name, key):
    """Remove the comment for a key."""
    try:
        remove_comment(get_env_dir(), env_name, key)
        click.echo(f"Comment removed for '{key}' in '{env_name}'.")
    except CommentError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@comment_group.command("list")
@click.argument("env_name")
def list_cmd(env_name):
    """List all comments for an env."""
    comments = list_comments(get_env_dir(), env_name)
    if not comments:
        click.echo("No comments found.")
        return
    for key, text in comments.items():
        click.echo(f"{key}: {text}")
