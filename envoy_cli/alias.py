"""Alias management: short names that map to env-name + profile combinations."""

from __future__ import annotations

import json
from pathlib import Path


class AliasError(Exception):
    pass


def _aliases_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / "aliases.json"


def _load_aliases(base_dir: str | Path) -> dict:
    p = _aliases_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(base_dir: str | Path, data: dict) -> None:
    p = _aliases_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_alias(base_dir: str | Path, alias: str, env_name: str, profile: str = "default") -> None:
    if not alias:
        raise AliasError("Alias name must not be empty.")
    if not env_name:
        raise AliasError("env_name must not be empty.")
    data = _load_aliases(base_dir)
    data[alias] = {"env_name": env_name, "profile": profile}
    _save_aliases(base_dir, data)


def get_alias(base_dir: str | Path, alias: str) -> dict:
    data = _load_aliases(base_dir)
    if alias not in data:
        raise AliasError(f"Alias '{alias}' not found.")
    return data[alias]


def remove_alias(base_dir: str | Path, alias: str) -> None:
    data = _load_aliases(base_dir)
    if alias not in data:
        raise AliasError(f"Alias '{alias}' not found.")
    del data[alias]
    _save_aliases(base_dir, data)


def list_aliases(base_dir: str | Path) -> dict:
    return _load_aliases(base_dir)


def rename_alias(base_dir: str | Path, old_alias: str, new_alias: str) -> None:
    """Rename an existing alias to a new name, preserving its target.

    Raises AliasError if old_alias does not exist or new_alias already exists.
    """
    if not new_alias:
        raise AliasError("New alias name must not be empty.")
    data = _load_aliases(base_dir)
    if old_alias not in data:
        raise AliasError(f"Alias '{old_alias}' not found.")
    if new_alias in data:
        raise AliasError(f"Alias '{new_alias}' already exists.")
    data[new_alias] = data.pop(old_alias)
    _save_aliases(base_dir, data)
