"""TTL (time-to-live) management for env entries."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional


class TTLError(Exception):
    pass


def _ttl_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "ttl.json"


def _load_ttl(base_dir: str) -> dict:
    p = _ttl_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(base_dir: str, data: dict) -> None:
    p = _ttl_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_ttl(base_dir: str, env_name: str, seconds: int) -> None:
    """Set a TTL for an env entry (expires_at = now + seconds)."""
    if not env_name:
        raise TTLError("env_name must not be empty")
    if seconds <= 0:
        raise TTLError("seconds must be a positive integer")
    data = _load_ttl(base_dir)
    data[env_name] = {"expires_at": time.time() + seconds, "seconds": seconds}
    _save_ttl(base_dir, data)


def get_ttl(base_dir: str, env_name: str) -> dict:
    """Return TTL info for env_name or raise TTLError."""
    data = _load_ttl(base_dir)
    if env_name not in data:
        raise TTLError(f"No TTL set for '{env_name}'")
    return data[env_name]


def is_expired(base_dir: str, env_name: str) -> bool:
    """Return True if the env TTL has passed, False if still valid or no TTL set."""
    data = _load_ttl(base_dir)
    if env_name not in data:
        return False
    return time.time() > data[env_name]["expires_at"]


def remove_ttl(base_dir: str, env_name: str) -> None:
    """Remove the TTL entry for env_name."""
    data = _load_ttl(base_dir)
    if env_name not in data:
        raise TTLError(f"No TTL set for '{env_name}'")
    del data[env_name]
    _save_ttl(base_dir, data)


def list_ttls(base_dir: str) -> list[dict]:
    """Return all TTL entries with expiry status."""
    data = _load_ttl(base_dir)
    now = time.time()
    return [
        {
            "env_name": name,
            "expires_at": info["expires_at"],
            "seconds": info["seconds"],
            "expired": now > info["expires_at"],
        }
        for name, info in data.items()
    ]
