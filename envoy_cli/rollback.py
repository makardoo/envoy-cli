"""Rollback support: revert an env to a previous snapshot or version."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envoy_cli.storage import load_env, save_env
from envoy_cli.snapshot import get_snapshot_dir, snapshot_path, SnapshotError


class RollbackError(Exception):
    pass


def _list_snapshot_names(base_dir: Path, env_name: str) -> list[str]:
    snap_dir = get_snapshot_dir(base_dir, env_name)
    if not snap_dir.exists():
        return []
    return sorted(
        p.stem for p in snap_dir.glob("*.json")
    )


def rollback_to_snapshot(
    base_dir: Path,
    env_name: str,
    snapshot_name: str,
    passphrase: str,
) -> str:
    """Restore env content from a named snapshot. Returns the restored content."""
    if not env_name:
        raise RollbackError("env_name must not be empty")
    path = snapshot_path(base_dir, env_name, snapshot_name)
    if not path.exists():
        raise RollbackError(f"Snapshot '{snapshot_name}' not found for env '{env_name}'")
    data = json.loads(path.read_text())
    content = data.get("content")
    if content is None:
        raise RollbackError(f"Snapshot '{snapshot_name}' is missing 'content' field")
    save_env(base_dir, env_name, content, passphrase)
    return content


def list_rollback_points(base_dir: Path, env_name: str) -> list[str]:
    """Return available snapshot names that can be rolled back to."""
    if not env_name:
        raise RollbackError("env_name must not be empty")
    return _list_snapshot_names(base_dir, env_name)


def latest_snapshot_name(base_dir: Path, env_name: str) -> Optional[str]:
    """Return the most recent snapshot name, or None if none exist."""
    names = _list_snapshot_names(base_dir, env_name)
    return names[-1] if names else None


def rollback_to_latest(
    base_dir: Path,
    env_name: str,
    passphrase: str,
) -> str:
    """Rollback to the most recent snapshot. Raises RollbackError if none exist."""
    name = latest_snapshot_name(base_dir, env_name)
    if name is None:
        raise RollbackError(f"No snapshots available for env '{env_name}'")
    return rollback_to_snapshot(base_dir, env_name, name, passphrase)
