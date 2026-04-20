"""Scope management for env files — assign and query deployment scopes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_SCOPES = {"local", "staging", "production", "global"}


class ScopeError(Exception):
    pass


def _scopes_path(base_dir: str) -> Path:
    return Path(base_dir) / "scopes.json"


def _load(base_dir: str) -> Dict[str, str]:
    p = _scopes_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, str]) -> None:
    p = _scopes_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_scope(base_dir: str, env_name: str, scope: str) -> None:
    """Assign a scope to an env file."""
    if not env_name:
        raise ScopeError("env_name must not be empty")
    if scope not in VALID_SCOPES:
        raise ScopeError(f"Invalid scope '{scope}'. Valid: {sorted(VALID_SCOPES)}")
    data = _load(base_dir)
    data[env_name] = scope
    _save(base_dir, data)


def get_scope(base_dir: str, env_name: str) -> str:
    """Return the scope assigned to an env file."""
    if not env_name:
        raise ScopeError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise ScopeError(f"No scope set for '{env_name}'")
    return data[env_name]


def remove_scope(base_dir: str, env_name: str) -> None:
    """Remove the scope assignment for an env file."""
    data = _load(base_dir)
    if env_name not in data:
        raise ScopeError(f"No scope set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_by_scope(base_dir: str, scope: str) -> List[str]:
    """Return all env names assigned to the given scope."""
    if scope not in VALID_SCOPES:
        raise ScopeError(f"Invalid scope '{scope}'. Valid: {sorted(VALID_SCOPES)}")
    data = _load(base_dir)
    return sorted(name for name, s in data.items() if s == scope)


def list_all_scopes(base_dir: str) -> Dict[str, str]:
    """Return a mapping of all env names to their scopes."""
    return dict(_load(base_dir))
