"""Friction tracking — record and query resistance/difficulty scores for env operations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List


class FrictionError(Exception):
    pass


VALID_LEVELS = ("none", "low", "medium", "high", "critical")


def _friction_path(base_dir: str) -> Path:
    return Path(base_dir) / "friction.json"


def _load(base_dir: str) -> Dict[str, Any]:
    p = _friction_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, Any]) -> None:
    p = _friction_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_friction(base_dir: str, name: str, level: str, reason: str = "") -> None:
    """Set the friction level for an env, with an optional reason."""
    if not name:
        raise FrictionError("env name must not be empty")
    if level not in VALID_LEVELS:
        raise FrictionError(f"invalid friction level '{level}'; choose from {VALID_LEVELS}")
    data = _load(base_dir)
    data[name] = {"level": level, "reason": reason}
    _save(base_dir, data)


def get_friction(base_dir: str, name: str) -> Dict[str, str]:
    """Return the friction record for an env."""
    if not name:
        raise FrictionError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise FrictionError(f"no friction record for '{name}'")
    return data[name]


def remove_friction(base_dir: str, name: str) -> None:
    """Remove the friction record for an env."""
    if not name:
        raise FrictionError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise FrictionError(f"no friction record for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_friction(base_dir: str) -> List[Dict[str, str]]:
    """Return all friction records as a list of dicts."""
    data = _load(base_dir)
    return [{"name": k, **v} for k, v in sorted(data.items())]
