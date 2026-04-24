"""Lifecycle state management for env files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_STATES = ["draft", "active", "deprecated", "archived", "retired"]
VALID_TRANSITIONS: Dict[str, List[str]] = {
    "draft":      ["active"],
    "active":     ["deprecated", "archived"],
    "deprecated": ["active", "retired"],
    "archived":   ["active", "retired"],
    "retired":    [],
}


class LifecycleError(Exception):
    pass


def _lifecycle_path(base_dir: Path) -> Path:
    return base_dir / ".envoy" / "lifecycle.json"


def _load(base_dir: Path) -> Dict[str, str]:
    p = _lifecycle_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: Dict[str, str]) -> None:
    p = _lifecycle_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_state(base_dir: Path, env_name: str, state: str) -> str:
    if not env_name:
        raise LifecycleError("env_name must not be empty")
    if state not in VALID_STATES:
        raise LifecycleError(f"Invalid state '{state}'. Must be one of: {VALID_STATES}")
    data = _load(base_dir)
    current = data.get(env_name)
    if current is not None:
        allowed = VALID_TRANSITIONS.get(current, [])
        if state not in allowed:
            raise LifecycleError(
                f"Cannot transition '{env_name}' from '{current}' to '{state}'. "
                f"Allowed transitions: {allowed}"
            )
    data[env_name] = state
    _save(base_dir, data)
    return state


def get_state(base_dir: Path, env_name: str) -> str:
    if not env_name:
        raise LifecycleError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise LifecycleError(f"No lifecycle state found for '{env_name}'")
    return data[env_name]


def remove_state(base_dir: Path, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise LifecycleError(f"No lifecycle state found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_states(base_dir: Path) -> Dict[str, str]:
    return _load(base_dir)
