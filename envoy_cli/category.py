"""Category management for env files."""
from __future__ import annotations
import json
from pathlib import Path


class CategoryError(Exception):
    pass


def _categories_path(base_dir: str) -> Path:
    return Path(base_dir) / "categories.json"


def _load(base_dir: str) -> dict:
    p = _categories_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _categories_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_category(base_dir: str, env_name: str, category: str) -> None:
    if not env_name:
        raise CategoryError("env_name must not be empty")
    if not category:
        raise CategoryError("category must not be empty")
    data = _load(base_dir)
    data[env_name] = category
    _save(base_dir, data)


def get_category(base_dir: str, env_name: str) -> str:
    data = _load(base_dir)
    if env_name not in data:
        raise CategoryError(f"No category set for '{env_name}'")
    return data[env_name]


def remove_category(base_dir: str, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise CategoryError(f"No category set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_by_category(base_dir: str, category: str) -> list[str]:
    data = _load(base_dir)
    return [name for name, cat in data.items() if cat == category]


def list_all_categories(base_dir: str) -> dict[str, str]:
    return _load(base_dir)
