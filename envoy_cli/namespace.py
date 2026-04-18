"""Namespace support: group env files under named namespaces (e.g. team, project)."""
from __future__ import annotations

import json
import os
from pathlib import Path

NAMESPACES_FILE = "namespaces.json"


class NamespaceError(Exception):
    pass


def _ns_path(base_dir: str) -> Path:
    return Path(base_dir) / NAMESPACES_FILE


def _load(base_dir: str) -> dict:
    p = _ns_path(base_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save(base_dir: str, data: dict) -> None:
    p = _ns_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


def assign_namespace(base_dir: str, env_name: str, namespace: str) -> None:
    """Assign an env to a namespace."""
    if not env_name:
        raise NamespaceError("env_name must not be empty")
    if not namespace:
        raise NamespaceError("namespace must not be empty")
    data = _load(base_dir)
    data[env_name] = namespace
    _save(base_dir, data)


def get_namespace(base_dir: str, env_name: str) -> str:
    """Return the namespace for an env, or raise NamespaceError."""
    data = _load(base_dir)
    if env_name not in data:
        raise NamespaceError(f"No namespace assigned to '{env_name}'")
    return data[env_name]


def remove_namespace(base_dir: str, env_name: str) -> None:
    """Remove the namespace assignment for an env."""
    data = _load(base_dir)
    if env_name not in data:
        raise NamespaceError(f"No namespace assigned to '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_by_namespace(base_dir: str, namespace: str) -> list[str]:
    """Return all env names assigned to a given namespace."""
    data = _load(base_dir)
    return sorted(k for k, v in data.items() if v == namespace)


def list_all_namespaces(base_dir: str) -> dict[str, list[str]]:
    """Return a mapping of namespace -> [env names]."""
    data = _load(base_dir)
    result: dict[str, list[str]] = {}
    for env_name, ns in data.items():
        result.setdefault(ns, []).append(env_name)
    for ns in result:
        result[ns].sort()
    return result
