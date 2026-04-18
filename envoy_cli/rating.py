"""Simple star-rating system for env entries."""
from __future__ import annotations

import json
from pathlib import Path


class RatingError(Exception):
    pass


def _ratings_path(base_dir: str) -> Path:
    return Path(base_dir) / "ratings.json"


def _load(base_dir: str) -> dict:
    p = _ratings_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _ratings_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_rating(base_dir: str, env_name: str, stars: int) -> None:
    """Set a star rating (1-5) for an env entry."""
    if not env_name:
        raise RatingError("env_name must not be empty")
    if not (1 <= stars <= 5):
        raise RatingError(f"stars must be between 1 and 5, got {stars}")
    data = _load(base_dir)
    data[env_name] = stars
    _save(base_dir, data)


def get_rating(base_dir: str, env_name: str) -> int:
    """Get the star rating for an env entry."""
    data = _load(base_dir)
    if env_name not in data:
        raise RatingError(f"No rating found for '{env_name}'")
    return data[env_name]


def remove_rating(base_dir: str, env_name: str) -> None:
    """Remove the rating for an env entry."""
    data = _load(base_dir)
    if env_name not in data:
        raise RatingError(f"No rating found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_ratings(base_dir: str) -> dict[str, int]:
    """Return all ratings as a dict of env_name -> stars."""
    return dict(_load(base_dir))
