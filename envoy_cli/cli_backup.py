"""CLI commands for backup/restore of env files."""
import os
import click
from envoy_cli.backup import BackupError, create_backup, list_backups, restore_backup, delete_backup
from envoy_cli.storage import load_env, save_env, get_env_dir


@click.group("backup")
def backup_group():
    """Backup and restore env files."""


@backup_group.command("create")
@click.argument("name")
@click.argument("label")
@click.option("--passphrase", envvar="ENVOY_PASSPHRASE", prompt=True, hide_input=True)
def create_cmd(name, label, passphrase):
    """Create a named backup of an env."""
    base = get_env_dir()
    try:
        content = load_env(name)
    except FileNotFoundError:
        click.echo(f"error: env '{name}' not found", err=True)
        raise SystemExit(1)
    try:
        path = create_backup(base, name, label, content)
        click.echo(f"backup '{label}' created at {path}")
    except BackupError as e:
        click.echo(f"error: {e}", err=True)
        raise SystemExit(1)


@backup_group.command("list")
@click.argument("name")
def list_cmd(name):
    """List backups for an env."""
    base = get_env_dir()
    backups = list_backups(base, name)
    if not backups:
        click.echo(f"no backups found for '{name}'")
        return
    for b in backups:
        click.echo(f"{b['label']:30s}  {b['created_at']}")


@backup_group.command("restore")
@click.argument("name")
@click.argument("label")
def restore_cmd(name, label):
    """Restore an env from a named backup."""
    base = get_env_dir()
    try:
        content = restore_backup(base, name, label)
        save_env(name, content)
        click.echo(f"env '{name}' restored from backup '{label}'")
    except BackupError as e:
        click.echo(f"error: {e}", err=True)
        raise SystemExit(1)


@backup_group.command("delete")
@click.argument("name")
@click.argument("label")
def delete_cmd(name, label):
    """Delete a named backup."""
    base = get_env_dir()
    try:
        delete_backup(base, name, label)
        click.echo(f"backup '{label}' deleted")
    except BackupError as e:
        click.echo(f"error: {e}", err=True)
        raise SystemExit(1)
