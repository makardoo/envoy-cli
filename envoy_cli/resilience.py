"""Resilience level tracking for env files."""
from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("fragile", "moderate", "robust", "hardened")


class ResilienceError(Exception):
    pass


def _resilience_path(base_dir: str) -> Path:
    return Path(base_dir) / "resilience.json"


def _load(base_dir: str) -> dict:
    p = _resilience_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _resilience_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_resilience(base_dir: str, name: str, level: str) -> None:
    """Set the resilience level for an env."""
    if not name:
        raise ResilienceError("env name must not be empty")
    if level not in VALID_LEVELS:
        raise ResilienceError(
            f"invalid level '{level}'; choose from {VALID_LEVELS}"
        )
    data = _load(base_dir)
    data[name] = level
    _save(base_dir, data)


def get_resilience(base_dir: str, name: str) -> str:
    """Return the resilience level for an env, defaulting to 'fragile'."""
    if not name:
        raise ResilienceError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        return "fragile"
    return data[name]


def remove_resilience(base_dir: str, name: str) -> None:
    """Remove the resilience record for an env."""
    data = _load(base_dir)
    if name not in data:
        raise ResilienceError(f"no resilience record for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_resilience(base_dir: str) -> dict:
    """Return all resilience records."""
    return _load(base_dir)
