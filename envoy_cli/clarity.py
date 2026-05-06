"""Clarity: assign a clarity level to env files indicating how well-documented they are."""

from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("opaque", "minimal", "documented", "exemplary")


class ClarityError(Exception):
    pass


def _clarity_path(base_dir: str) -> Path:
    return Path(base_dir) / "clarity.json"


def _load(base_dir: str) -> dict:
    p = _clarity_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _clarity_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_clarity(base_dir: str, env_name: str, level: str, note: str = "") -> None:
    if not env_name:
        raise ClarityError("env_name must not be empty")
    if level not in VALID_LEVELS:
        raise ClarityError(f"Invalid clarity level '{level}'. Choose from: {', '.join(VALID_LEVELS)}")
    data = _load(base_dir)
    data[env_name] = {"level": level, "note": note}
    _save(base_dir, data)


def get_clarity(base_dir: str, env_name: str) -> dict:
    if not env_name:
        raise ClarityError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise ClarityError(f"No clarity record found for '{env_name}'")
    return data[env_name]


def remove_clarity(base_dir: str, env_name: str) -> None:
    if not env_name:
        raise ClarityError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise ClarityError(f"No clarity record found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_clarity(base_dir: str) -> dict:
    return _load(base_dir)
