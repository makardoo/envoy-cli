"""Impact level tracking for env files."""
from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("low", "medium", "high", "critical")


class ImpactError(Exception):
    pass


def _impact_path(base_dir: str) -> Path:
    return Path(base_dir) / "impact.json"


def _load(base_dir: str) -> dict:
    p = _impact_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _impact_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_impact(base_dir: str, name: str, level: str) -> None:
    """Assign an impact level to an env."""
    if not name:
        raise ImpactError("env name must not be empty")
    if level not in VALID_LEVELS:
        raise ImpactError(
            f"invalid impact level '{level}'; choose from {VALID_LEVELS}"
        )
    data = _load(base_dir)
    data[name] = level
    _save(base_dir, data)


def get_impact(base_dir: str, name: str, default: str = "low") -> str:
    """Return the impact level for an env, or *default* if not set."""
    if not name:
        raise ImpactError("env name must not be empty")
    data = _load(base_dir)
    return data.get(name, default)


def remove_impact(base_dir: str, name: str) -> None:
    """Remove the impact entry for an env."""
    data = _load(base_dir)
    if name not in data:
        raise ImpactError(f"no impact level set for '{name}'")
    del data[name]
    _save(base_dir, data)


def list_impact(base_dir: str) -> dict:
    """Return all impact entries."""
    return _load(base_dir)
