"""Cadence tracking: how often an env is expected to be updated."""
from __future__ import annotations

import json
from pathlib import Path

VALID_CADENCES = ("hourly", "daily", "weekly", "monthly", "manual")


class CadenceError(Exception):
    pass


def _cadence_path(base_dir: str) -> Path:
    return Path(base_dir) / "cadence.json"


def _load(base_dir: str) -> dict:
    p = _cadence_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _cadence_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_cadence(base_dir: str, env_name: str, cadence: str) -> None:
    """Assign an update cadence to an env."""
    if not env_name:
        raise CadenceError("env_name must not be empty")
    if cadence not in VALID_CADENCES:
        raise CadenceError(
            f"Invalid cadence '{cadence}'. Choose from: {', '.join(VALID_CADENCES)}"
        )
    data = _load(base_dir)
    data[env_name] = cadence
    _save(base_dir, data)


def get_cadence(base_dir: str, env_name: str) -> str:
    """Return the cadence for an env, defaulting to 'manual'."""
    if not env_name:
        raise CadenceError("env_name must not be empty")
    data = _load(base_dir)
    return data.get(env_name, "manual")


def remove_cadence(base_dir: str, env_name: str) -> None:
    """Remove cadence entry for an env."""
    data = _load(base_dir)
    if env_name not in data:
        raise CadenceError(f"No cadence set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_cadences(base_dir: str) -> dict:
    """Return all cadence assignments."""
    return _load(base_dir)
