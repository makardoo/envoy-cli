"""Archive (soft-delete) and restore env entries."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any


class ArchiveError(Exception):
    pass


def _archive_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "archive.json"


def _load(base_dir: str) -> Dict[str, Any]:
    p = _archive_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, Any]) -> None:
    p = _archive_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def archive_env(base_dir: str, env_name: str, content: str) -> None:
    """Move an env entry into the archive store."""
    if not env_name:
        raise ArchiveError("env_name must not be empty")
    data = _load(base_dir)
    if env_name in data:
        raise ArchiveError(f"'{env_name}' is already archived")
    data[env_name] = {"content": content}
    _save(base_dir, data)


def restore_env(base_dir: str, env_name: str) -> str:
    """Restore an archived env entry and return its content."""
    data = _load(base_dir)
    if env_name not in data:
        raise ArchiveError(f"'{env_name}' not found in archive")
    content = data.pop(env_name)["content"]
    _save(base_dir, data)
    return content


def list_archived(base_dir: str) -> List[str]:
    """Return names of all archived envs."""
    return sorted(_load(base_dir).keys())


def delete_archived(base_dir: str, env_name: str) -> None:
    """Permanently delete an archived env entry."""
    data = _load(base_dir)
    if env_name not in data:
        raise ArchiveError(f"'{env_name}' not found in archive")
    del data[env_name]
    _save(base_dir, data)
