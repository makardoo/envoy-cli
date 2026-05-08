"""Track and query obsolescence status of env files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class ObsolescenceError(Exception):
    """Raised when an obsolescence operation fails."""


def _obsolescence_path(base_dir: str) -> Path:
    return Path(base_dir) / "obsolescence.json"


def _load(base_dir: str) -> dict:
    p = _obsolescence_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _obsolescence_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def mark_obsolete(base_dir: str, name: str, reason: str = "") -> dict:
    """Mark an env as obsolete, recording the timestamp and optional reason."""
    if not name:
        raise ObsolescenceError("env name must not be empty")
    data = _load(base_dir)
    entry = {
        "obsolete": True,
        "reason": reason,
        "marked_at": datetime.now(timezone.utc).isoformat(),
    }
    data[name] = entry
    _save(base_dir, data)
    return entry


def unmark_obsolete(base_dir: str, name: str) -> None:
    """Remove the obsolescence mark from an env."""
    if not name:
        raise ObsolescenceError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise ObsolescenceError(f"env '{name}' is not marked as obsolete")
    del data[name]
    _save(base_dir, data)


def get_obsolescence(base_dir: str, name: str) -> dict:
    """Return the obsolescence record for *name*, or raise if not found."""
    if not name:
        raise ObsolescenceError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise ObsolescenceError(f"env '{name}' has no obsolescence record")
    return data[name]


def list_obsolete(base_dir: str) -> list[str]:
    """Return a sorted list of env names that are marked obsolete."""
    return sorted(_load(base_dir).keys())
