"""Manage favorite (starred) env names for quick access."""

from __future__ import annotations

import json
from pathlib import Path


class FavoriteError(Exception):
    pass


def _favorites_path(base_dir: str) -> Path:
    return Path(base_dir) / "favorites.json"


def _load(base_dir: str) -> list[str]:
    p = _favorites_path(base_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(base_dir: str, favorites: list[str]) -> None:
    p = _favorites_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(favorites, indent=2))


def add_favorite(base_dir: str, env_name: str) -> None:
    if not env_name:
        raise FavoriteError("env_name must not be empty")
    favorites = _load(base_dir)
    if env_name in favorites:
        raise FavoriteError(f"'{env_name}' is already a favorite")
    favorites.append(env_name)
    _save(base_dir, favorites)


def remove_favorite(base_dir: str, env_name: str) -> None:
    favorites = _load(base_dir)
    if env_name not in favorites:
        raise FavoriteError(f"'{env_name}' is not a favorite")
    favorites.remove(env_name)
    _save(base_dir, favorites)


def list_favorites(base_dir: str) -> list[str]:
    return _load(base_dir)


def is_favorite(base_dir: str, env_name: str) -> bool:
    return env_name in _load(base_dir)
