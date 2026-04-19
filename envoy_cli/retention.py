"""Retention policy management for env files."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


class RetentionError(Exception):
    pass


def _retention_path(base_dir: str) -> Path:
    return Path(base_dir) / "retention.json"


def _load(base_dir: str) -> dict:
    p = _retention_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _retention_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_retention(base_dir: str, env_name: str, days: int) -> None:
    if not env_name:
        raise RetentionError("env_name must not be empty")
    if days <= 0:
        raise RetentionError("days must be a positive integer")
    data = _load(base_dir)
    data[env_name] = {"days": days, "set_at": datetime.utcnow().isoformat()}
    _save(base_dir, data)


def get_retention(base_dir: str, env_name: str) -> dict:
    data = _load(base_dir)
    if env_name not in data:
        raise RetentionError(f"No retention policy found for '{env_name}'")
    return data[env_name]


def remove_retention(base_dir: str, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise RetentionError(f"No retention policy found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_retention(base_dir: str) -> list[dict]:
    data = _load(base_dir)
    return [{"env_name": k, **v} for k, v in data.items()]


def is_expired(base_dir: str, env_name: str, reference: Optional[datetime] = None) -> bool:
    entry = get_retention(base_dir, env_name)
    set_at = datetime.fromisoformat(entry["set_at"])
    expiry = set_at + timedelta(days=entry["days"])
    now = reference or datetime.utcnow()
    return now >= expiry
