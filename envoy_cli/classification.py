"""Classification module for envoy-cli.

Allows assigning a data classification level to an environment
(e.g. public, internal, confidential, restricted).
"""
from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("public", "internal", "confidential", "restricted")


class ClassificationError(Exception):
    """Raised when a classification operation fails."""


def _classification_path(base_dir: str) -> Path:
    return Path(base_dir) / "classifications.json"


def _load(base_dir: str) -> dict:
    p = _classification_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _classification_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_classification(base_dir: str, env_name: str, level: str) -> None:
    """Assign a classification level to *env_name*."""
    if not env_name:
        raise ClassificationError("env_name must not be empty")
    if level not in VALID_LEVELS:
        raise ClassificationError(
            f"Invalid classification level '{level}'. "
            f"Choose from: {', '.join(VALID_LEVELS)}"
        )
    data = _load(base_dir)
    data[env_name] = level
    _save(base_dir, data)


def get_classification(base_dir: str, env_name: str) -> str:
    """Return the classification level for *env_name*.

    Raises ClassificationError if no level has been set.
    """
    if not env_name:
        raise ClassificationError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise ClassificationError(
            f"No classification set for environment '{env_name}'"
        )
    return data[env_name]


def remove_classification(base_dir: str, env_name: str) -> None:
    """Remove the classification entry for *env_name*."""
    data = _load(base_dir)
    if env_name not in data:
        raise ClassificationError(
            f"No classification set for environment '{env_name}'"
        )
    del data[env_name]
    _save(base_dir, data)


def list_classifications(base_dir: str) -> dict:
    """Return a mapping of env_name -> classification level."""
    return dict(_load(base_dir))
