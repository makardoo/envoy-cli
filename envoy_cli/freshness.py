"""Track and check the freshness (last-updated timestamp) of env files."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


class FreshnessError(Exception):
    """Raised on freshness-related errors."""


def _freshness_path(base_dir: str) -> Path:
    return Path(base_dir) / "freshness.json"


def _load(base_dir: str) -> dict:
    p = _freshness_path(base_dir)
    if not p.exists():
        return {}
    with p.open() as fh:
        return json.load(fh)


def _save(base_dir: str, data: dict) -> None:
    p = _freshness_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as fh:
        json.dump(data, fh, indent=2)


def touch(base_dir: str, env_name: str) -> str:
    """Record the current UTC timestamp as the last-updated time for *env_name*.

    Returns the ISO-formatted timestamp that was recorded.
    """
    if not env_name or not env_name.strip():
        raise FreshnessError("env_name must not be empty")
    data = _load(base_dir)
    ts = datetime.now(timezone.utc).isoformat()
    data[env_name] = ts
    _save(base_dir, data)
    return ts


def get_freshness(base_dir: str, env_name: str) -> str:
    """Return the ISO timestamp of the last update for *env_name*.

    Raises FreshnessError if no record exists.
    """
    if not env_name or not env_name.strip():
        raise FreshnessError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise FreshnessError(f"No freshness record for '{env_name}'")
    return data[env_name]


def is_stale(base_dir: str, env_name: str, max_age_seconds: int) -> bool:
    """Return True if *env_name* has not been updated within *max_age_seconds*.

    Raises FreshnessError if no record exists.
    """
    if max_age_seconds < 0:
        raise FreshnessError("max_age_seconds must be >= 0")
    ts = get_freshness(base_dir, env_name)
    updated = datetime.fromisoformat(ts)
    age = (datetime.now(timezone.utc) - updated).total_seconds()
    return age > max_age_seconds


def remove_freshness(base_dir: str, env_name: str) -> None:
    """Delete the freshness record for *env_name*.

    Raises FreshnessError if no record exists.
    """
    data = _load(base_dir)
    if env_name not in data:
        raise FreshnessError(f"No freshness record for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_freshness(base_dir: str) -> dict:
    """Return all freshness records as {env_name: iso_timestamp}."""
    return _load(base_dir)
