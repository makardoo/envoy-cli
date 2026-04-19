"""Version tracking for env files."""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import List, Dict, Any


class VersionError(Exception):
    pass


def _version_dir(base_dir: str) -> Path:
    p = Path(base_dir) / ".versions"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _version_path(base_dir: str, env_name: str) -> Path:
    return _version_dir(base_dir) / f"{env_name}.json"


def _load(base_dir: str, env_name: str) -> List[Dict[str, Any]]:
    p = _version_path(base_dir, env_name)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(base_dir: str, env_name: str, versions: List[Dict[str, Any]]) -> None:
    _version_path(base_dir, env_name).write_text(json.dumps(versions, indent=2))


def record_version(base_dir: str, env_name: str, content: str, message: str = "") -> Dict[str, Any]:
    if not env_name.strip():
        raise VersionError("env_name must not be empty")
    versions = _load(base_dir, env_name)
    number = len(versions) + 1
    entry: Dict[str, Any] = {
        "version": number,
        "timestamp": time.time(),
        "message": message,
        "content": content,
    }
    versions.append(entry)
    _save(base_dir, env_name, versions)
    return entry


def list_versions(base_dir: str, env_name: str) -> List[Dict[str, Any]]:
    return _load(base_dir, env_name)


def get_version(base_dir: str, env_name: str, number: int) -> Dict[str, Any]:
    versions = _load(base_dir, env_name)
    for v in versions:
        if v["version"] == number:
            return v
    raise VersionError(f"Version {number} not found for '{env_name}'")


def delete_versions(base_dir: str, env_name: str) -> None:
    p = _version_path(base_dir, env_name)
    if p.exists():
        p.unlink()
