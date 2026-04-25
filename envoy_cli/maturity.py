"""Maturity level tracking for env files."""
from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("experimental", "beta", "stable", "deprecated")


class MaturityError(Exception):
    """Raised when a maturity operation fails."""


def _maturity_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / "maturity.json"


def _load(base_dir: str | Path) -> dict:
    p = _maturity_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str | Path, data: dict) -> None:
    p = _maturity_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_maturity(base_dir: str | Path, env_name: str, level: str) -> None:
    """Assign a maturity level to an env."""
    if not env_name:
        raise MaturityError("env_name must not be empty")
    if level not in VALID_LEVELS:
        raise MaturityError(
            f"Invalid level '{level}'. Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load(base_dir)
    data[env_name] = level
    _save(base_dir, data)


def get_maturity(base_dir: str | Path, env_name: str) -> str:
    """Return the maturity level for an env."""
    if not env_name:
        raise MaturityError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise MaturityError(f"No maturity level set for '{env_name}'")
    return data[env_name]


def remove_maturity(base_dir: str | Path, env_name: str) -> None:
    """Remove the maturity level for an env."""
    if not env_name:
        raise MaturityError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise MaturityError(f"No maturity level set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_maturity(base_dir: str | Path) -> dict[str, str]:
    """Return all env maturity levels."""
    return dict(_load(base_dir))
