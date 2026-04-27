"""Endorsement module: track peer approvals for env configs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class EndorsementError(Exception):
    pass


def _endorsements_path(base_dir: str) -> Path:
    return Path(base_dir) / "endorsements.json"


def _load(base_dir: str) -> Dict[str, List[str]]:
    p = _endorsements_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, List[str]]) -> None:
    p = _endorsements_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_endorsement(base_dir: str, env_name: str, endorser: str) -> List[str]:
    """Add an endorser to an env. Duplicates are ignored."""
    if not env_name:
        raise EndorsementError("env_name must not be empty")
    if not endorser:
        raise EndorsementError("endorser must not be empty")
    data = _load(base_dir)
    current = data.get(env_name, [])
    if endorser not in current:
        current.append(endorser)
    data[env_name] = current
    _save(base_dir, data)
    return current


def remove_endorsement(base_dir: str, env_name: str, endorser: str) -> List[str]:
    """Remove an endorser from an env."""
    data = _load(base_dir)
    current = data.get(env_name, [])
    if endorser not in current:
        raise EndorsementError(f"Endorser '{endorser}' not found for env '{env_name}'")
    current = [e for e in current if e != endorser]
    data[env_name] = current
    _save(base_dir, data)
    return current


def get_endorsements(base_dir: str, env_name: str) -> List[str]:
    """Return list of endorsers for an env."""
    return _load(base_dir).get(env_name, [])


def list_all_endorsements(base_dir: str) -> Dict[str, List[str]]:
    """Return the full endorsement map."""
    return _load(base_dir)
