"""Spotlight: mark and retrieve featured/highlighted env files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class SpotlightError(Exception):
    """Raised when a spotlight operation fails."""


def _spotlight_path(base_dir: str) -> Path:
    return Path(base_dir) / "spotlights.json"


def _load(base_dir: str) -> Dict[str, str]:
    p = _spotlight_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, str]) -> None:
    p = _spotlight_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def spotlight_env(base_dir: str, name: str, reason: str = "") -> None:
    """Mark an env as spotlighted with an optional reason."""
    if not name:
        raise SpotlightError("env name must not be empty")
    data = _load(base_dir)
    data[name] = reason
    _save(base_dir, data)


def remove_spotlight(base_dir: str, name: str) -> None:
    """Remove spotlight from an env."""
    data = _load(base_dir)
    if name not in data:
        raise SpotlightError(f"env '{name}' is not spotlighted")
    del data[name]
    _save(base_dir, data)


def get_spotlight(base_dir: str, name: str) -> str:
    """Return the reason an env is spotlighted."""
    data = _load(base_dir)
    if name not in data:
        raise SpotlightError(f"env '{name}' is not spotlighted")
    return data[name]


def list_spotlights(base_dir: str) -> List[Dict[str, str]]:
    """Return all spotlighted envs as a list of dicts."""
    data = _load(base_dir)
    return [{"name": k, "reason": v} for k, v in data.items()]
