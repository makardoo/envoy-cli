"""Risk level management for env files."""

from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("low", "medium", "high", "critical")


class RiskError(Exception):
    pass


def _risk_path(base_dir: str) -> Path:
    return Path(base_dir) / "risk.json"


def _load(base_dir: str) -> dict:
    p = _risk_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _risk_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_risk(base_dir: str, name: str, level: str, note: str = "") -> None:
    """Assign a risk level to an env."""
    if not name:
        raise RiskError("env name must not be empty")
    if level not in VALID_LEVELS:
        raise RiskError(f"invalid risk level '{level}'; choose from {VALID_LEVELS}")
    data = _load(base_dir)
    data[name] = {"level": level, "note": note}
    _save(base_dir, data)


def get_risk(base_dir: str, name: str) -> dict:
    """Return risk info for an env; default level is 'low'."""
    data = _load(base_dir)
    if name not in data:
        return {"level": "low", "note": ""}
    return data[name]


def remove_risk(base_dir: str, name: str) -> None:
    """Remove risk record for an env."""
    data = _load(base_dir)
    if name not in data:
        raise RiskError(f"no risk record for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_risks(base_dir: str) -> dict:
    """Return all risk records."""
    return _load(base_dir)
