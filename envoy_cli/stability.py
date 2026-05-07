"""Stability tracking for env files."""
from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("unstable", "experimental", "stable", "frozen")


class StabilityError(Exception):
    pass


def _stability_path(base_dir: str) -> Path:
    return Path(base_dir) / "stability.json"


def _load(base_dir: str) -> dict:
    p = _stability_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _stability_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_stability(base_dir: str, name: str, level: str) -> None:
    """Set the stability level for an env."""
    if not name:
        raise StabilityError("env name must not be empty")
    if level not in VALID_LEVELS:
        raise StabilityError(
            f"invalid stability level '{level}'; choose from {VALID_LEVELS}"
        )
    data = _load(base_dir)
    data[name] = level
    _save(base_dir, data)


def get_stability(base_dir: str, name: str) -> str:
    """Return the stability level for an env, defaulting to 'unstable'."""
    if not name:
        raise StabilityError("env name must not be empty")
    data = _load(base_dir)
    return data.get(name, "unstable")


def remove_stability(base_dir: str, name: str) -> None:
    """Remove the stability record for an env."""
    data = _load(base_dir)
    if name not in data:
        raise StabilityError(f"no stability record for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_stability(base_dir: str) -> dict:
    """Return all recorded stability levels."""
    return _load(base_dir)
