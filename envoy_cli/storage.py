"""Storage module for reading and writing encrypted .env files to disk."""

import os
from pathlib import Path
from typing import Optional

DEFAULT_ENV_DIR = Path.home() / ".envoy"
ENV_FILE_EXTENSION = ".enc"


def get_env_dir(base_dir: Optional[Path] = None) -> Path:
    """Return the directory used to store encrypted env files."""
    return base_dir or DEFAULT_ENV_DIR


def ensure_env_dir(base_dir: Optional[Path] = None) -> Path:
    """Create the env storage directory if it doesn't exist."""
    env_dir = get_env_dir(base_dir)
    env_dir.mkdir(parents=True, exist_ok=True)
    return env_dir


def env_file_path(name: str, base_dir: Optional[Path] = None) -> Path:
    """Return the full path for a named encrypted env file."""
    env_dir = get_env_dir(base_dir)
    safe_name = name.replace("/", "_").replace("\\", "_")
    return env_dir / f"{safe_name}{ENV_FILE_EXTENSION}"


def save_env(name: str, encrypted_content: str, base_dir: Optional[Path] = None) -> Path:
    """Write encrypted env content to disk under the given name.

    Args:
        name: Logical name for the env (e.g. 'production', 'staging').
        encrypted_content: The encrypted string to persist.
        base_dir: Optional override for the storage directory.

    Returns:
        The path where the file was written.
    """
    ensure_env_dir(base_dir)
    path = env_file_path(name, base_dir)
    path.write_text(encrypted_content, encoding="utf-8")
    return path


def load_env(name: str, base_dir: Optional[Path] = None) -> str:
    """Read encrypted env content from disk for the given name.

    Args:
        name: Logical name for the env.
        base_dir: Optional override for the storage directory.

    Returns:
        The raw encrypted string stored on disk.

    Raises:
        FileNotFoundError: If no env file exists for the given name.
    """
    path = env_file_path(name, base_dir)
    if not path.exists():
        raise FileNotFoundError(f"No env file found for '{name}' at {path}")
    return path.read_text(encoding="utf-8")


def list_envs(base_dir: Optional[Path] = None) -> list[str]:
    """List all stored env names."""
    env_dir = get_env_dir(base_dir)
    if not env_dir.exists():
        return []
    return [
        p.stem
        for p in sorted(env_dir.iterdir())
        if p.suffix == ENV_FILE_EXTENSION
    ]


def delete_env(name: str, base_dir: Optional[Path] = None) -> bool:
    """Delete a stored env file. Returns True if deleted, False if not found."""
    path = env_file_path(name, base_dir)
    if path.exists():
        path.unlink()
        return True
    return False
