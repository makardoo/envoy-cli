"""Checksum tracking for env files to detect tampering or unexpected changes."""

import hashlib
import json
from pathlib import Path
from typing import Optional


class ChecksumError(Exception):
    pass


def _checksum_path(base_dir: str) -> Path:
    return Path(base_dir) / ".checksums.json"


def _load(base_dir: str) -> dict:
    p = _checksum_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _checksum_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def compute_checksum(content: str) -> str:
    """Return SHA-256 hex digest of content."""
    return hashlib.sha256(content.encode()).hexdigest()


def record_checksum(base_dir: str, env_name: str, content: str) -> str:
    """Compute and store checksum for env_name. Returns the checksum."""
    if not env_name:
        raise ChecksumError("env_name must not be empty")
    checksum = compute_checksum(content)
    data = _load(base_dir)
    data[env_name] = checksum
    _save(base_dir, data)
    return checksum


def get_checksum(base_dir: str, env_name: str) -> str:
    """Retrieve stored checksum for env_name."""
    data = _load(base_dir)
    if env_name not in data:
        raise ChecksumError(f"No checksum recorded for '{env_name}'")
    return data[env_name]


def verify_checksum(base_dir: str, env_name: str, content: str) -> bool:
    """Return True if content matches stored checksum, False otherwise."""
    try:
        stored = get_checksum(base_dir, env_name)
    except ChecksumError:
        return False
    return compute_checksum(content) == stored


def remove_checksum(base_dir: str, env_name: str) -> None:
    """Remove stored checksum for env_name."""
    data = _load(base_dir)
    if env_name not in data:
        raise ChecksumError(f"No checksum recorded for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_checksums(base_dir: str) -> dict:
    """Return all stored checksums as {env_name: checksum}."""
    return _load(base_dir)
