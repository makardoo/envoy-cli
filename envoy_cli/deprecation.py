"""Track and query deprecation notices for env files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class DeprecationError(Exception):
    pass


def _deprecations_path(base_dir: str) -> Path:
    return Path(base_dir) / "deprecations.json"


def _load(base_dir: str) -> dict:
    p = _deprecations_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _deprecations_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def deprecate_env(
    base_dir: str,
    name: str,
    reason: str = "",
    replacement: Optional[str] = None,
) -> dict:
    """Mark an env as deprecated, optionally pointing to a replacement."""
    if not name:
        raise DeprecationError("env name must not be empty")
    data = _load(base_dir)
    entry = {
        "deprecated_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "replacement": replacement,
    }
    data[name] = entry
    _save(base_dir, data)
    return entry


def get_deprecation(base_dir: str, name: str) -> dict:
    """Return the deprecation record for *name*, raising if absent."""
    if not name:
        raise DeprecationError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise DeprecationError(f"no deprecation notice found for '{name}'")
    return data[name]


def remove_deprecation(base_dir: str, name: str) -> None:
    """Remove a deprecation notice (un-deprecate)."""
    if not name:
        raise DeprecationError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise DeprecationError(f"no deprecation notice found for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_deprecations(base_dir: str) -> list[dict]:
    """Return all deprecation records as a list of dicts with 'name' included."""
    data = _load(base_dir)
    return [{"name": k, **v} for k, v in data.items()]


def is_deprecated(base_dir: str, name: str) -> bool:
    """Return True if *name* has an active deprecation notice."""
    data = _load(base_dir)
    return name in data
