"""CLI commands for the watch feature."""
from __future__ import annotations
import click
from envoy_cli.watch import watch_file, build_sync_callback, WatchError
from envoy_cli.storage import get_env_dir


@click.group("watch")
def watch_group() -> None:
    """Watch a .env file and auto-sync on change."""


@watch_group.command("start")
@click.argument("env_name")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--passphrase", prompt=True, hide_input=True, help="Encryption passphrase.")
@click.option("--remote-dir", default=None, help="Remote directory for sync.")
@click.option("--interval", default=2.0, show_default=True, help="Poll interval in seconds.")
def start(
    env_name: str,
    filepath: str,
    passphrase: str,
    remote_dir: str | None,
    interval: float,
) -> None:
    """Watch FILEPATH and push ENV_NAME to remote on every change."""
    local_dir = get_env_dir()
    effective_remote = remote_dir or (local_dir + "_remote")

    callback = build_sync_callback(
        env_name=env_name,
        passphrase=passphrase,
        remote_dir=effective_remote,
        local_dir=local_dir,
    )

    click.echo(f"Watching {filepath} for changes (interval={interval}s). Press Ctrl+C to stop.")
    try:
        watch_file(filepath, on_change=callback, interval=interval)
    except WatchError as exc:
        raise click.ClickException(str(exc))
    except KeyboardInterrupt:
        click.echo("\nWatch stopped.")
