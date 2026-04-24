"""Cooldown management for env operations.

Prevents rapid repeated writes/pushes to an environment within a
configurable cooldown window (in seconds).
"""
from __future__ import annotations

import json
import time
from pathlib import Path


class CooldownError(Exception):
    """Raised when a cooldown-related operation fails."""


DEFAULT_COOLDOWN_SECONDS = 60


def _cooldown_path(base_dir: Path) -> Path:
    return base_dir / "cooldowns.json"


def _load(base_dir: Path) -> dict:
    p = _cooldown_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: dict) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _cooldown_path(base_dir).write_text(json.dumps(data, indent=2))


def set_cooldown(base_dir: Path, env_name: str, seconds: int) -> None:
    """Set the cooldown window (in seconds) for *env_name*."""
    if not env_name:
        raise CooldownError("env_name must not be empty")
    if seconds < 0:
        raise CooldownError("seconds must be >= 0")
    data = _load(base_dir)
    data[env_name] = {"seconds": seconds}
    _save(base_dir, data)


def get_cooldown(base_dir: Path, env_name: str) -> int:
    """Return the configured cooldown window for *env_name* in seconds."""
    if not env_name:
        raise CooldownError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise CooldownError(f"No cooldown configured for '{env_name}'")
    return data[env_name]["seconds"]


def remove_cooldown(base_dir: Path, env_name: str) -> None:
    """Remove the cooldown configuration for *env_name*."""
    data = _load(base_dir)
    if env_name not in data:
        raise CooldownError(f"No cooldown configured for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def record_access(base_dir: Path, env_name: str) -> float:
    """Record the current timestamp as the last access time for *env_name*."""
    if not env_name:
        raise CooldownError("env_name must not be empty")
    data = _load(base_dir)
    entry = data.get(env_name, {})
    now = time.time()
    entry["last_access"] = now
    data[env_name] = entry
    _save(base_dir, data)
    return now


def check_cooldown(base_dir: Path, env_name: str) -> None:
    """Raise CooldownError if *env_name* is still within its cooldown window."""
    data = _load(base_dir)
    entry = data.get(env_name, {})
    seconds = entry.get("seconds", DEFAULT_COOLDOWN_SECONDS)
    last = entry.get("last_access")
    if last is None:
        return
    elapsed = time.time() - last
    if elapsed < seconds:
        remaining = int(seconds - elapsed)
        raise CooldownError(
            f"'{env_name}' is in cooldown. "
            f"Wait {remaining}s before the next operation."
        )


def list_cooldowns(base_dir: Path) -> list[dict]:
    """Return all configured cooldowns as a list of dicts."""
    data = _load(base_dir)
    result = []
    for name, entry in data.items():
        result.append({
            "env": name,
            "seconds": entry.get("seconds", DEFAULT_COOLDOWN_SECONDS),
            "last_access": entry.get("last_access"),
        })
    return result
