"""Ownership tracking for env files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class OwnershipError(Exception):
    pass


def _ownership_path(base_dir: Path) -> Path:
    return base_dir / "ownership.json"


def _load(base_dir: Path) -> Dict[str, Dict]:
    p = _ownership_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: Dict[str, Dict]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _ownership_path(base_dir).write_text(json.dumps(data, indent=2))


def set_owner(base_dir: Path, env_name: str, owner: str, team: Optional[str] = None) -> None:
    """Assign an owner (and optionally a team) to an env."""
    if not env_name:
        raise OwnershipError("env_name must not be empty")
    if not owner:
        raise OwnershipError("owner must not be empty")
    data = _load(base_dir)
    data[env_name] = {"owner": owner, "team": team}
    _save(base_dir, data)


def get_owner(base_dir: Path, env_name: str) -> Dict:
    """Return ownership info for an env."""
    data = _load(base_dir)
    if env_name not in data:
        raise OwnershipError(f"No ownership record for '{env_name}'")
    return data[env_name]


def remove_owner(base_dir: Path, env_name: str) -> None:
    """Remove ownership record for an env."""
    data = _load(base_dir)
    if env_name not in data:
        raise OwnershipError(f"No ownership record for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_owned(base_dir: Path, owner: Optional[str] = None, team: Optional[str] = None) -> List[str]:
    """List env names, optionally filtered by owner or team."""
    data = _load(base_dir)
    results = []
    for env_name, info in data.items():
        if owner and info.get("owner") != owner:
            continue
        if team and info.get("team") != team:
            continue
        results.append(env_name)
    return sorted(results)
