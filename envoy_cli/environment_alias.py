"""Environment alias resolution — map short names to full env identifiers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class EnvAliasError(Exception):
    """Raised for environment alias operation failures."""


def _alias_map_path(base_dir: str) -> Path:
    return Path(base_dir) / "env_aliases.json"


def _load(base_dir: str) -> Dict[str, str]:
    p = _alias_map_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, str]) -> None:
    p = _alias_map_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_env_alias(base_dir: str, alias: str, env_name: str) -> None:
    """Map *alias* to *env_name*."""
    if not alias:
        raise EnvAliasError("Alias must not be empty.")
    if not env_name:
        raise EnvAliasError("env_name must not be empty.")
    data = _load(base_dir)
    data[alias] = env_name
    _save(base_dir, data)


def resolve_env_alias(base_dir: str, alias: str) -> str:
    """Return the env_name mapped to *alias*, or raise if not found."""
    data = _load(base_dir)
    if alias not in data:
        raise EnvAliasError(f"Alias '{alias}' not found.")
    return data[alias]


def remove_env_alias(base_dir: str, alias: str) -> None:
    """Remove an alias mapping."""
    data = _load(base_dir)
    if alias not in data:
        raise EnvAliasError(f"Alias '{alias}' not found.")
    del data[alias]
    _save(base_dir, data)


def list_env_aliases(base_dir: str) -> List[Dict[str, str]]:
    """Return all alias mappings as a list of dicts."""
    data = _load(base_dir)
    return [{"alias": k, "env_name": v} for k, v in sorted(data.items())]
