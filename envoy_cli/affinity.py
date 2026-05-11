"""Affinity module — track which environments are related or paired."""
from __future__ import annotations

import json
from pathlib import Path


class AffinityError(Exception):
    pass


def _affinity_path(base_dir: str) -> Path:
    return Path(base_dir) / "affinity.json"


def _load(base_dir: str) -> dict:
    p = _affinity_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _affinity_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_affinity(base_dir: str, env_name: str, related: str, strength: str = "weak") -> None:
    """Record that *env_name* has affinity with *related*."""
    if not env_name:
        raise AffinityError("env_name must not be empty")
    if not related:
        raise AffinityError("related must not be empty")
    valid = {"weak", "moderate", "strong"}
    if strength not in valid:
        raise AffinityError(f"strength must be one of {sorted(valid)}, got {strength!r}")
    data = _load(base_dir)
    data.setdefault(env_name, {})
    data[env_name][related] = strength
    _save(base_dir, data)


def get_affinity(base_dir: str, env_name: str, related: str) -> str:
    """Return the affinity strength between *env_name* and *related*."""
    data = _load(base_dir)
    try:
        return data[env_name][related]
    except KeyError:
        raise AffinityError(f"No affinity recorded between {env_name!r} and {related!r}")


def remove_affinity(base_dir: str, env_name: str, related: str) -> None:
    """Remove affinity link between *env_name* and *related*."""
    data = _load(base_dir)
    if env_name not in data or related not in data.get(env_name, {}):
        raise AffinityError(f"No affinity recorded between {env_name!r} and {related!r}")
    del data[env_name][related]
    if not data[env_name]:
        del data[env_name]
    _save(base_dir, data)


def list_affinities(base_dir: str, env_name: str) -> dict:
    """Return all affinities for *env_name* as {related: strength}."""
    data = _load(base_dir)
    return dict(data.get(env_name, {}))


def list_all(base_dir: str) -> dict:
    """Return the full affinity map."""
    return _load(base_dir)
