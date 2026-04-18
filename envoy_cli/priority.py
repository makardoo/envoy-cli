"""Priority management for env files."""
from __future__ import annotations

import json
from pathlib import Path


class PriorityError(Exception):
    pass


def _priority_path(base_dir: str) -> Path:
    return Path(base_dir) / "priorities.json"


def _load(base_dir: str) -> dict:
    p = _priority_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _priority_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_priority(base_dir: str, env_name: str, priority: int) -> None:
    if not env_name:
        raise PriorityError("env_name must not be empty")
    if not isinstance(priority, int):
        raise PriorityError("priority must be an integer")
    data = _load(base_dir)
    data[env_name] = priority
    _save(base_dir, data)


def get_priority(base_dir: str, env_name: str) -> int:
    data = _load(base_dir)
    if env_name not in data:
        raise PriorityError(f"No priority set for '{env_name}'")
    return data[env_name]


def remove_priority(base_dir: str, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise PriorityError(f"No priority set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_priorities(base_dir: str) -> list[tuple[str, int]]:
    data = _load(base_dir)
    return sorted(data.items(), key=lambda x: x[1], reverse=True)
