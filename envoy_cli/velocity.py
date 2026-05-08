"""Track and report the rate of change (velocity) for env files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


class VelocityError(Exception):
    """Raised when a velocity operation fails."""


def _velocity_path(base_dir: Path) -> Path:
    return base_dir / "velocity.json"


def _load(base_dir: Path) -> Dict[str, List[str]]:
    p = _velocity_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: Dict[str, List[str]]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _velocity_path(base_dir).write_text(json.dumps(data, indent=2))


def record_change(base_dir: Path, env_name: str) -> str:
    """Record a change event for *env_name*; returns the ISO timestamp."""
    if not env_name:
        raise VelocityError("env_name must not be empty")
    data = _load(base_dir)
    ts = datetime.now(timezone.utc).isoformat()
    data.setdefault(env_name, []).append(ts)
    _save(base_dir, data)
    return ts


def get_changes(base_dir: Path, env_name: str) -> List[str]:
    """Return all recorded change timestamps for *env_name*."""
    if not env_name:
        raise VelocityError("env_name must not be empty")
    return _load(base_dir).get(env_name, [])


def compute_velocity(base_dir: Path, env_name: str) -> Dict[str, Any]:
    """Return a summary dict with total changes and changes in last 24 h."""
    changes = get_changes(base_dir, env_name)
    now = datetime.now(timezone.utc)
    recent = [
        ts for ts in changes
        if (now - datetime.fromisoformat(ts)).total_seconds() <= 86400
    ]
    return {
        "env_name": env_name,
        "total": len(changes),
        "last_24h": len(recent),
        "last_change": changes[-1] if changes else None,
    }


def clear_changes(base_dir: Path, env_name: str) -> None:
    """Remove all recorded changes for *env_name*."""
    if not env_name:
        raise VelocityError("env_name must not be empty")
    data = _load(base_dir)
    data.pop(env_name, None)
    _save(base_dir, data)
