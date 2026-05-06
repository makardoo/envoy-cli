"""Readiness module — track whether an env is ready for use/deployment."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

VALID_STATES = {"ready", "not_ready", "pending", "blocked"}


class ReadinessError(Exception):
    pass


def _readiness_path(base_dir: str) -> Path:
    return Path(base_dir) / "readiness.json"


def _load(base_dir: str) -> Dict[str, dict]:
    p = _readiness_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, dict]) -> None:
    p = _readiness_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_readiness(base_dir: str, env_name: str, state: str, reason: Optional[str] = None) -> None:
    """Set the readiness state for an env."""
    if not env_name:
        raise ReadinessError("env_name must not be empty")
    if state not in VALID_STATES:
        raise ReadinessError(f"Invalid state '{state}'. Must be one of: {sorted(VALID_STATES)}")
    data = _load(base_dir)
    data[env_name] = {"state": state, "reason": reason or ""}
    _save(base_dir, data)


def get_readiness(base_dir: str, env_name: str) -> dict:
    """Return the readiness record for an env."""
    if not env_name:
        raise ReadinessError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise ReadinessError(f"No readiness record found for '{env_name}'")
    return data[env_name]


def remove_readiness(base_dir: str, env_name: str) -> None:
    """Remove the readiness record for an env."""
    data = _load(base_dir)
    if env_name not in data:
        raise ReadinessError(f"No readiness record found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_readiness(base_dir: str) -> Dict[str, dict]:
    """Return all readiness records."""
    return _load(base_dir)
