"""Watch a local .env file for changes and auto-sync to remote."""
from __future__ import annotations
import time
import os
from pathlib import Path
from typing import Callable, Optional


class WatchError(Exception):
    pass


def _mtime(path: str) -> float:
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return 0.0


def watch_file(
    filepath: str,
    on_change: Callable[[str], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *filepath* every *interval* seconds; call *on_change* with the path on modification."""
    if not Path(filepath).exists():
        raise WatchError(f"File not found: {filepath}")

    last_mtime = _mtime(filepath)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        current_mtime = _mtime(filepath)
        if current_mtime != last_mtime:
            last_mtime = current_mtime
            on_change(filepath)
        iterations += 1


def build_sync_callback(
    env_name: str,
    passphrase: str,
    remote_dir: str,
    local_dir: str,
) -> Callable[[str], None]:
    """Return a callback that pushes the env file to remote when called."""
    from envoy_cli.sync import push_env

    def _callback(path: str) -> None:
        content = Path(path).read_text()
        push_env(env_name, content, passphrase, remote_dir=remote_dir, local_dir=local_dir)

    return _callback
