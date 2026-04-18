"""Track dependencies between env files (e.g. staging depends on base)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class DependencyError(Exception):
    pass


def _deps_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "dependencies.json"


def _load(base_dir: str) -> Dict[str, List[str]]:
    p = _deps_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, List[str]]) -> None:
    p = _deps_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_dependency(base_dir: str, env_name: str, depends_on: str) -> None:
    """Register that env_name depends on depends_on."""
    if not env_name:
        raise DependencyError("env_name must not be empty")
    if not depends_on:
        raise DependencyError("depends_on must not be empty")
    if env_name == depends_on:
        raise DependencyError("An env cannot depend on itself")
    data = _load(base_dir)
    deps = data.setdefault(env_name, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save(base_dir, data)


def remove_dependency(base_dir: str, env_name: str, depends_on: str) -> None:
    data = _load(base_dir)
    deps = data.get(env_name, [])
    if depends_on not in deps:
        raise DependencyError(f"'{env_name}' does not depend on '{depends_on}'")
    deps.remove(depends_on)
    if not deps:
        del data[env_name]
    _save(base_dir, data)


def get_dependencies(base_dir: str, env_name: str) -> List[str]:
    return _load(base_dir).get(env_name, [])


def list_all_dependencies(base_dir: str) -> Dict[str, List[str]]:
    return _load(base_dir)


def detect_cycle(base_dir: str, env_name: str, depends_on: str) -> bool:
    """Return True if adding env_name -> depends_on would create a cycle."""
    data = _load(base_dir)
    visited: set = set()
    queue = [depends_on]
    while queue:
        node = queue.pop()
        if node == env_name:
            return True
        if node in visited:
            continue
        visited.add(node)
        queue.extend(data.get(node, []))
    return False
