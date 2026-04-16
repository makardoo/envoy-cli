"""Lock/unlock mechanism to prevent accidental writes to env files."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envoy_cli.storage import get_env_dir

LOCK_FILE_NAME = ".envoy_locks.json"


class LockError(Exception):
    """Raised when a lock operation fails."""


def _lock_file_path(env_dir: Optional[str] = None) -> Path:
    base = Path(env_dir) if env_dir else get_env_dir()
    return base / LOCK_FILE_NAME


def _load_locks(env_dir: Optional[str] = None) -> dict:
    path = _lock_file_path(env_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_locks(locks: dict, env_dir: Optional[str] = None) -> None:
    path = _lock_file_path(env_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(locks, f, indent=2)


def lock_env(env_name: str, reason: str = "", env_dir: Optional[str] = None) -> None:
    """Lock an env file to prevent modifications."""
    if not env_name:
        raise LockError("env_name must not be empty")
    locks = _load_locks(env_dir)
    if env_name in locks:
        raise LockError(f"'{env_name}' is already locked")
    locks[env_name] = {
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    _save_locks(locks, env_dir)


def unlock_env(env_name: str, env_dir: Optional[str] = None) -> None:
    """Unlock a previously locked env file."""
    locks = _load_locks(env_dir)
    if env_name not in locks:
        raise LockError(f"'{env_name}' is not locked")
    del locks[env_name]
    _save_locks(locks, env_dir)


def is_locked(env_name: str, env_dir: Optional[str] = None) -> bool:
    """Return True if the given env is locked."""
    locks = _load_locks(env_dir)
    return env_name in locks


def get_lock_info(env_name: str, env_dir: Optional[str] = None) -> Optional[dict]:
    """Return lock metadata for an env, or None if not locked."""
    locks = _load_locks(env_dir)
    return locks.get(env_name)


def list_locked_envs(env_dir: Optional[str] = None) -> dict:
    """Return all locked envs and their metadata."""
    return _load_locks(env_dir)
