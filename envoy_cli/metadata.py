"""Attach arbitrary key-value metadata to env names."""
from __future__ import annotations

import json
from pathlib import Path


class MetadataError(Exception):
    pass


def _meta_path(base_dir: str) -> Path:
    return Path(base_dir) / "metadata.json"


def _load(base_dir: str) -> dict:
    p = _meta_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _meta_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_metadata(base_dir: str, env_name: str, key: str, value: str) -> None:
    if not env_name:
        raise MetadataError("env_name must not be empty")
    if not key:
        raise MetadataError("key must not be empty")
    data = _load(base_dir)
    data.setdefault(env_name, {})[key] = value
    _save(base_dir, data)


def get_metadata(base_dir: str, env_name: str, key: str) -> str:
    data = _load(base_dir)
    try:
        return data[env_name][key]
    except KeyError:
        raise MetadataError(f"No metadata key '{key}' for env '{env_name}'")


def get_all_metadata(base_dir: str, env_name: str) -> dict:
    data = _load(base_dir)
    return dict(data.get(env_name, {}))


def remove_metadata(base_dir: str, env_name: str, key: str) -> None:
    data = _load(base_dir)
    if env_name not in data or key not in data[env_name]:
        raise MetadataError(f"No metadata key '{key}' for env '{env_name}'")
    del data[env_name][key]
    if not data[env_name]:
        del data[env_name]
    _save(base_dir, data)


def list_all_metadata(base_dir: str) -> dict:
    return _load(base_dir)
