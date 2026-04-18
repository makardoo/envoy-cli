"""Quota management: limit the number of env entries stored per environment."""
from __future__ import annotations

import json
from pathlib import Path


class QuotaError(Exception):
    pass


def _quota_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "quotas.json"


def _load(base_dir: str) -> dict:
    p = _quota_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _quota_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_quota(base_dir: str, env_name: str, limit: int) -> None:
    """Set a maximum number of keys allowed for an env."""
    if not env_name:
        raise QuotaError("env_name must not be empty")
    if limit < 1:
        raise QuotaError("limit must be at least 1")
    data = _load(base_dir)
    data[env_name] = limit
    _save(base_dir, data)


def get_quota(base_dir: str, env_name: str) -> int:
    """Return the quota for an env, or raise if not set."""
    data = _load(base_dir)
    if env_name not in data:
        raise QuotaError(f"No quota set for '{env_name}'")
    return data[env_name]


def remove_quota(base_dir: str, env_name: str) -> None:
    """Remove the quota for an env."""
    data = _load(base_dir)
    if env_name not in data:
        raise QuotaError(f"No quota set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_quotas(base_dir: str) -> dict:
    """Return all quotas as {env_name: limit}."""
    return _load(base_dir)


def check_quota(base_dir: str, env_name: str, current_count: int) -> None:
    """Raise QuotaError if current_count exceeds the quota for env_name."""
    data = _load(base_dir)
    if env_name not in data:
        return
    limit = data[env_name]
    if current_count > limit:
        raise QuotaError(
            f"Quota exceeded for '{env_name}': {current_count} keys > limit {limit}"
        )
