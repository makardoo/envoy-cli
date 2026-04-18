"""Inline comment support for .env files."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional

COMMENT_SUFFIX = ".comments.json"


class CommentError(Exception):
    pass


def _comments_path(base_dir: str, env_name: str) -> Path:
    return Path(base_dir) / f"{env_name}{COMMENT_SUFFIX}"


def _load(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save(path: Path, data: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def set_comment(base_dir: str, env_name: str, key: str, comment: str) -> None:
    if not env_name:
        raise CommentError("env_name must not be empty")
    if not key:
        raise CommentError("key must not be empty")
    path = _comments_path(base_dir, env_name)
    data = _load(path)
    data[key] = comment
    _save(path, data)


def get_comment(base_dir: str, env_name: str, key: str) -> str:
    path = _comments_path(base_dir, env_name)
    data = _load(path)
    if key not in data:
        raise CommentError(f"No comment for key '{key}' in env '{env_name}'")
    return data[key]


def remove_comment(base_dir: str, env_name: str, key: str) -> None:
    path = _comments_path(base_dir, env_name)
    data = _load(path)
    if key not in data:
        raise CommentError(f"No comment for key '{key}' in env '{env_name}'")
    del data[key]
    _save(path, data)


def list_comments(base_dir: str, env_name: str) -> Dict[str, str]:
    path = _comments_path(base_dir, env_name)
    return _load(path)
