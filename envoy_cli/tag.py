"""Tagging support for named env snapshots/aliases."""
from __future__ import annotations

import json
from pathlib import Path

TAGS_FILE = "tags.json"


class TagError(Exception):
    pass


def _tags_path(base_dir: str) -> Path:
    return Path(base_dir) / TAGS_FILE


def _load_tags(base_dir: str) -> dict:
    p = _tags_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_tags(base_dir: str, tags: dict) -> None:
    p = _tags_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(tags, indent=2))


def add_tag(base_dir: str, tag: str, env_name: str, ref: str) -> None:
    """Associate a tag with an env name and an arbitrary ref (e.g. snapshot path)."""
    if not tag:
        raise TagError("Tag name must not be empty.")
    if not env_name:
        raise TagError("Env name must not be empty.")
    tags = _load_tags(base_dir)
    tags[tag] = {"env": env_name, "ref": ref}
    _save_tags(base_dir, tags)


def remove_tag(base_dir: str, tag: str) -> None:
    tags = _load_tags(base_dir)
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found.")
    del tags[tag]
    _save_tags(base_dir, tags)


def get_tag(base_dir: str, tag: str) -> dict:
    tags = _load_tags(base_dir)
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found.")
    return tags[tag]


def list_tags(base_dir: str) -> list[dict]:
    tags = _load_tags(base_dir)
    return [{"tag": k, **v} for k, v in sorted(tags.items())]
