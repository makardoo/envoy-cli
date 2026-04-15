"""Snapshot module: create and restore point-in-time snapshots of env files."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Dict, Any

from envoy_cli.storage import get_env_dir, load_env, save_env


SNAPSHOT_DIR_NAME = "snapshots"


class SnapshotError(Exception):
    pass


def get_snapshot_dir(base_dir: str | None = None) -> Path:
    """Return the directory used to store snapshots."""
    env_dir = Path(base_dir) if base_dir else get_env_dir()
    snapshot_dir = env_dir / SNAPSHOT_DIR_NAME
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    return snapshot_dir


def snapshot_path(env_name: str, timestamp: int, base_dir: str | None = None) -> Path:
    """Return the file path for a specific snapshot."""
    return get_snapshot_dir(base_dir) / f"{env_name}_{timestamp}.snap"


def create_snapshot(env_name: str, base_dir: str | None = None) -> Path:
    """Create a snapshot of the current encrypted env file.

    Returns the path to the created snapshot file.
    Raises SnapshotError if the env does not exist.
    """
    try:
        content = load_env(env_name, base_dir=base_dir)
    except FileNotFoundError:
        raise SnapshotError(f"Environment '{env_name}' not found; cannot snapshot.")

    ts = int(time.time())
    path = snapshot_path(env_name, ts, base_dir=base_dir)
    meta: Dict[str, Any] = {
        "env_name": env_name,
        "timestamp": ts,
        "content": content,
    }
    path.write_text(json.dumps(meta), encoding="utf-8")
    return path


def list_snapshots(env_name: str, base_dir: str | None = None) -> List[Dict[str, Any]]:
    """Return a list of snapshot metadata dicts for *env_name*, oldest first."""
    snap_dir = get_snapshot_dir(base_dir)
    results = []
    for p in sorted(snap_dir.glob(f"{env_name}_*.snap")):
        try:
            meta = json.loads(p.read_text(encoding="utf-8"))
            results.append(meta)
        except (json.JSONDecodeError, OSError):
            continue
    return results


def restore_snapshot(env_name: str, timestamp: int, base_dir: str | None = None) -> None:
    """Restore an env file from a snapshot identified by *timestamp*.

    Raises SnapshotError if the snapshot does not exist.
    """
    path = snapshot_path(env_name, timestamp, base_dir=base_dir)
    if not path.exists():
        raise SnapshotError(
            f"Snapshot for '{env_name}' at timestamp {timestamp} not found."
        )
    meta = json.loads(path.read_text(encoding="utf-8"))
    save_env(env_name, meta["content"], base_dir=base_dir)
