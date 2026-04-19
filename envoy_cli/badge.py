"""Badge module: assign and manage status badges for env files."""

from __future__ import annotations

import json
from pathlib import Path

VALID_BADGES = {"stable", "experimental", "deprecated", "wip", "reviewed"}


class BadgeError(Exception):
    pass


def _badges_path(base_dir: str) -> Path:
    return Path(base_dir) / "badges.json"


def _load(base_dir: str) -> dict:
    p = _badges_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _badges_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_badge(base_dir: str, env_name: str, badge: str) -> None:
    if not env_name:
        raise BadgeError("env_name must not be empty")
    if badge not in VALID_BADGES:
        raise BadgeError(f"Invalid badge '{badge}'. Valid: {sorted(VALID_BADGES)}")
    data = _load(base_dir)
    data[env_name] = badge
    _save(base_dir, data)


def get_badge(base_dir: str, env_name: str) -> str:
    data = _load(base_dir)
    if env_name not in data:
        raise BadgeError(f"No badge set for '{env_name}'")
    return data[env_name]


def remove_badge(base_dir: str, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise BadgeError(f"No badge set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_badges(base_dir: str) -> dict:
    return _load(base_dir)
