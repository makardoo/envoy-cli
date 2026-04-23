"""Manage environment type classifications (e.g. local, staging, production)."""
from __future__ import annotations

import json
from pathlib import Path

VALID_TYPES = {"local", "staging", "production", "testing", "development"}


class EnvironmentTypeError(Exception):
    pass


def _type_path(base_dir: str) -> Path:
    return Path(base_dir) / "env_types.json"


def _load(base_dir: str) -> dict:
    p = _type_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _type_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_env_type(base_dir: str, env_name: str, env_type: str) -> None:
    """Assign a type to an env file."""
    if not env_name:
        raise EnvironmentTypeError("env_name must not be empty")
    if env_type not in VALID_TYPES:
        raise EnvironmentTypeError(
            f"Invalid type '{env_type}'. Valid types: {sorted(VALID_TYPES)}"
        )
    data = _load(base_dir)
    data[env_name] = env_type
    _save(base_dir, data)


def get_env_type(base_dir: str, env_name: str) -> str:
    """Return the type assigned to an env file."""
    data = _load(base_dir)
    if env_name not in data:
        raise EnvironmentTypeError(f"No type set for env '{env_name}'")
    return data[env_name]


def remove_env_type(base_dir: str, env_name: str) -> None:
    """Remove the type assignment for an env file."""
    data = _load(base_dir)
    if env_name not in data:
        raise EnvironmentTypeError(f"No type set for env '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_env_types(base_dir: str) -> dict:
    """Return all env-name -> type mappings."""
    return _load(base_dir)
