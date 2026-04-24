"""Expiry management for env entries — set, get, check, and clear expiry dates."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


class ExpiryError(Exception):
    pass


def _expiry_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / "expiry.json"


def _load(base_dir: str | Path) -> dict:
    p = _expiry_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str | Path, data: dict) -> None:
    p = _expiry_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_expiry(base_dir: str | Path, env_name: str, expires_at: datetime) -> None:
    """Set an expiry datetime (UTC) for an env entry."""
    if not env_name:
        raise ExpiryError("env_name must not be empty")
    data = _load(base_dir)
    data[env_name] = expires_at.strftime(DATE_FMT)
    _save(base_dir, data)


def get_expiry(base_dir: str | Path, env_name: str) -> datetime:
    """Return the expiry datetime for an env entry."""
    data = _load(base_dir)
    if env_name not in data:
        raise ExpiryError(f"No expiry set for '{env_name}'")
    return datetime.strptime(data[env_name], DATE_FMT).replace(tzinfo=timezone.utc)


def remove_expiry(base_dir: str | Path, env_name: str) -> None:
    """Remove the expiry for an env entry."""
    data = _load(base_dir)
    if env_name not in data:
        raise ExpiryError(f"No expiry set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def is_expired(base_dir: str | Path, env_name: str) -> bool:
    """Return True if the env entry has passed its expiry date."""
    try:
        exp = get_expiry(base_dir, env_name)
    except ExpiryError:
        return False
    return datetime.now(tz=timezone.utc) >= exp


def list_expiries(base_dir: str | Path) -> dict[str, datetime]:
    """Return all expiry entries as a dict of name -> datetime."""
    data = _load(base_dir)
    return {
        k: datetime.strptime(v, DATE_FMT).replace(tzinfo=timezone.utc)
        for k, v in data.items()
    }
