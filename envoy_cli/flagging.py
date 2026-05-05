"""Flag envs for review or attention."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class FlaggingError(Exception):
    pass


def _flags_path(base_dir: str) -> Path:
    return Path(base_dir) / "flags.json"


def _load(base_dir: str) -> Dict[str, dict]:
    p = _flags_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, dict]) -> None:
    p = _flags_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def flag_env(base_dir: str, name: str, reason: str = "") -> None:
    """Flag an env for review."""
    if not name:
        raise FlaggingError("env name must not be empty")
    data = _load(base_dir)
    data[name] = {"reason": reason, "flagged": True}
    _save(base_dir, data)


def unflag_env(base_dir: str, name: str) -> None:
    """Remove the flag from an env."""
    if not name:
        raise FlaggingError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise FlaggingError(f"env '{name}' is not flagged")
    del data[name]
    _save(base_dir, data)


def get_flag(base_dir: str, name: str) -> Optional[dict]:
    """Return flag info for an env, or None if not flagged."""
    if not name:
        raise FlaggingError("env name must not be empty")
    data = _load(base_dir)
    return data.get(name)


def list_flagged(base_dir: str) -> List[str]:
    """Return list of all flagged env names."""
    return list(_load(base_dir).keys())
