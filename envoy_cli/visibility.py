"""Visibility settings for env files (public, private, internal)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

VALID_LEVELS = {"public", "private", "internal"}


class VisibilityError(Exception):
    pass


def _visibility_path(base_dir: Path) -> Path:
    return base_dir / ".envoy" / "visibility.json"


def _load(base_dir: Path) -> Dict[str, str]:
    path = _visibility_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(base_dir: Path, data: Dict[str, str]) -> None:
    path = _visibility_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_visibility(base_dir: Path, env_name: str, level: str) -> None:
    """Set the visibility level for an env."""
    if not env_name:
        raise VisibilityError("env_name must not be empty")
    if level not in VALID_LEVELS:
        raise VisibilityError(
            f"Invalid visibility level '{level}'. Must be one of: {sorted(VALID_LEVELS)}"
        )
    data = _load(base_dir)
    data[env_name] = level
    _save(base_dir, data)


def get_visibility(base_dir: Path, env_name: str) -> str:
    """Get the visibility level for an env. Defaults to 'private'."""
    if not env_name:
        raise VisibilityError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        return "private"
    return data[env_name]


def remove_visibility(base_dir: Path, env_name: str) -> None:
    """Remove the visibility setting for an env."""
    if not env_name:
        raise VisibilityError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise VisibilityError(f"No visibility setting found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_visibility(base_dir: Path) -> Dict[str, str]:
    """Return all visibility settings."""
    return _load(base_dir)
