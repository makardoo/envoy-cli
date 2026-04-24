"""Sensitivity classification for .env entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_LEVELS = ("public", "internal", "confidential", "secret")


class SensitivityError(Exception):
    pass


def _sensitivity_path(base_dir: str) -> Path:
    return Path(base_dir) / "sensitivity.json"


def _load(base_dir: str) -> Dict[str, str]:
    path = _sensitivity_path(base_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(base_dir: str, data: Dict[str, str]) -> None:
    path = _sensitivity_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_sensitivity(base_dir: str, env_name: str, level: str) -> None:
    """Assign a sensitivity level to an env entry."""
    if not env_name:
        raise SensitivityError("env_name must not be empty")
    if level not in VALID_LEVELS:
        raise SensitivityError(
            f"Invalid level '{level}'. Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load(base_dir)
    data[env_name] = level
    _save(base_dir, data)


def get_sensitivity(base_dir: str, env_name: str) -> str:
    """Return the sensitivity level for an env entry."""
    data = _load(base_dir)
    if env_name not in data:
        raise SensitivityError(f"No sensitivity level set for '{env_name}'")
    return data[env_name]


def remove_sensitivity(base_dir: str, env_name: str) -> None:
    """Remove sensitivity classification for an env entry."""
    data = _load(base_dir)
    if env_name not in data:
        raise SensitivityError(f"No sensitivity level set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_sensitivity(base_dir: str) -> List[Dict[str, str]]:
    """Return all sensitivity classifications as a list of dicts."""
    data = _load(base_dir)
    return [{"env": k, "level": v} for k, v in sorted(data.items())]


def get_sensitivity_default(base_dir: str, env_name: str, default: str = "internal") -> str:
    """Return sensitivity level or a default if not set."""
    try:
        return get_sensitivity(base_dir, env_name)
    except SensitivityError:
        return default
