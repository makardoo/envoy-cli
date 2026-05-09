"""Longevity tracking for env files — records creation date and computes age."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class LongevityError(Exception):
    """Raised when a longevity operation fails."""


def _longevity_path(base_dir: Path) -> Path:
    return base_dir / "longevity.json"


def _load(base_dir: Path) -> dict:
    p = _longevity_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: dict) -> None:
    p = _longevity_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def record_creation(base_dir: Path, name: str) -> str:
    """Record the creation timestamp for *name*. Returns the ISO timestamp."""
    if not name:
        raise LongevityError("env name must not be empty")
    data = _load(base_dir)
    if name in data:
        return data[name]["created_at"]
    ts = datetime.now(timezone.utc).isoformat()
    data[name] = {"created_at": ts}
    _save(base_dir, data)
    return ts


def get_longevity(base_dir: Path, name: str) -> dict:
    """Return longevity info for *name*, including age in days."""
    if not name:
        raise LongevityError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise LongevityError(f"no longevity record for '{name}'")
    created_at = data[name]["created_at"]
    created_dt = datetime.fromisoformat(created_at)
    now = datetime.now(timezone.utc)
    age_days = (now - created_dt).days
    return {"name": name, "created_at": created_at, "age_days": age_days}


def delete_longevity(base_dir: Path, name: str) -> None:
    """Remove the longevity record for *name*."""
    if not name:
        raise LongevityError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise LongevityError(f"no longevity record for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_longevity(base_dir: Path) -> list[dict]:
    """Return longevity info for all tracked envs, sorted by age descending."""
    data = _load(base_dir)
    results = []
    now = datetime.now(timezone.utc)
    for name, entry in data.items():
        created_dt = datetime.fromisoformat(entry["created_at"])
        age_days = (now - created_dt).days
        results.append({"name": name, "created_at": entry["created_at"], "age_days": age_days})
    return sorted(results, key=lambda r: r["age_days"], reverse=True)
