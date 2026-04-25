"""Trust level management for env files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

TRUST_LEVELS = ("untrusted", "low", "medium", "high", "verified")


class TrustError(Exception):
    pass


def _trust_path(base_dir: str) -> Path:
    return Path(base_dir) / "trust.json"


def _load(base_dir: str) -> Dict[str, str]:
    p = _trust_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, str]) -> None:
    p = _trust_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_trust(base_dir: str, name: str, level: str) -> None:
    """Assign a trust level to an env file."""
    if not name:
        raise TrustError("env name must not be empty")
    if level not in TRUST_LEVELS:
        raise TrustError(
            f"invalid trust level '{level}'; choose from {list(TRUST_LEVELS)}"
        )
    data = _load(base_dir)
    data[name] = level
    _save(base_dir, data)


def get_trust(base_dir: str, name: str) -> str:
    """Return the trust level for an env, defaulting to 'untrusted'."""
    if not name:
        raise TrustError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        return "untrusted"
    return data[name]


def remove_trust(base_dir: str, name: str) -> None:
    """Remove trust assignment for an env."""
    if not name:
        raise TrustError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        raise TrustError(f"no trust record for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_trust(base_dir: str) -> List[Dict[str, str]]:
    """List all trust assignments."""
    data = _load(base_dir)
    return [{"name": k, "level": v} for k, v in sorted(data.items())]
