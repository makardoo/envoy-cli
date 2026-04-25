"""Track parent/child relationships between env files (lineage)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class LineageError(Exception):
    """Raised for lineage-related errors."""


def _lineage_path(base_dir: str) -> Path:
    return Path(base_dir) / "lineage.json"


def _load(base_dir: str) -> Dict[str, dict]:
    p = _lineage_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, dict]) -> None:
    p = _lineage_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_parent(base_dir: str, env_name: str, parent_name: str) -> None:
    """Declare *parent_name* as the parent of *env_name*."""
    if not env_name:
        raise LineageError("env_name must not be empty")
    if not parent_name:
        raise LineageError("parent_name must not be empty")
    if env_name == parent_name:
        raise LineageError("An environment cannot be its own parent")
    data = _load(base_dir)
    entry = data.get(env_name, {})
    entry["parent"] = parent_name
    data[env_name] = entry
    _save(base_dir, data)


def get_parent(base_dir: str, env_name: str) -> str:
    """Return the parent of *env_name*, or raise LineageError if not set."""
    data = _load(base_dir)
    entry = data.get(env_name, {})
    if "parent" not in entry:
        raise LineageError(f"No parent set for '{env_name}'")
    return entry["parent"]


def remove_parent(base_dir: str, env_name: str) -> None:
    """Remove the parent relationship for *env_name*."""
    data = _load(base_dir)
    entry = data.get(env_name, {})
    if "parent" not in entry:
        raise LineageError(f"No parent set for '{env_name}'")
    del entry["parent"]
    if entry:
        data[env_name] = entry
    else:
        del data[env_name]
    _save(base_dir, data)


def get_children(base_dir: str, parent_name: str) -> List[str]:
    """Return all env names whose parent is *parent_name*."""
    data = _load(base_dir)
    return [
        name for name, entry in data.items()
        if entry.get("parent") == parent_name
    ]


def get_ancestors(base_dir: str, env_name: str) -> List[str]:
    """Return ordered list of ancestors (parent, grandparent, …)."""
    ancestors: List[str] = []
    visited = set()
    current: Optional[str] = env_name
    while True:
        data = _load(base_dir)
        entry = data.get(current, {})
        parent = entry.get("parent")
        if parent is None:
            break
        if parent in visited:
            raise LineageError(f"Cycle detected in lineage near '{parent}'")
        visited.add(parent)
        ancestors.append(parent)
        current = parent
    return ancestors
