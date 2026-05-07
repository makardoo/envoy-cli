"""Track and report usage momentum (activity frequency) for env entries."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class MomentumError(Exception):
    pass


def _momentum_path(base_dir: Path) -> Path:
    return base_dir / "momentum.json"


def _load(base_dir: Path) -> Dict[str, List[str]]:
    p = _momentum_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: Dict[str, List[str]]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _momentum_path(base_dir).write_text(json.dumps(data, indent=2))


def record_access(base_dir: Path, name: str) -> str:
    """Record a timestamped access event for *name*. Returns the ISO timestamp."""
    if not name or not name.strip():
        raise MomentumError("env name must not be empty")
    data = _load(base_dir)
    ts = datetime.now(timezone.utc).isoformat()
    data.setdefault(name, []).append(ts)
    _save(base_dir, data)
    return ts


def get_accesses(base_dir: Path, name: str) -> List[str]:
    """Return all recorded access timestamps for *name*."""
    if not name or not name.strip():
        raise MomentumError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise MomentumError(f"no momentum data for env '{name}'")
    return list(data[name])


def get_count(base_dir: Path, name: str) -> int:
    """Return the total number of accesses for *name*."""
    return len(get_accesses(base_dir, name))


def clear_momentum(base_dir: Path, name: str) -> None:
    """Remove all momentum data for *name*."""
    if not name or not name.strip():
        raise MomentumError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise MomentumError(f"no momentum data for env '{name}'")
    del data[name]
    _save(base_dir, data)


def list_momentum(base_dir: Path) -> Dict[str, int]:
    """Return a mapping of env name -> access count for all tracked envs."""
    data = _load(base_dir)
    return {name: len(timestamps) for name, timestamps in data.items()}
