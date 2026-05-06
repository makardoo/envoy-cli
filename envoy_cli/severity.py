"""Severity levels for env files."""
from __future__ import annotations

import json
from pathlib import Path

VALID_LEVELS = ("low", "medium", "high", "critical")


class SeverityError(Exception):
    pass


def _severity_path(base_dir: str) -> Path:
    return Path(base_dir) / "severity.json"


def _load(base_dir: str) -> dict:
    p = _severity_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _severity_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_severity(base_dir: str, name: str, level: str) -> None:
    """Assign a severity level to an env."""
    if not name:
        raise SeverityError("env name must not be empty")
    if level not in VALID_LEVELS:
        raise SeverityError(
            f"invalid severity level {level!r}; choose from {VALID_LEVELS}"
        )
    data = _load(base_dir)
    data[name] = level
    _save(base_dir, data)


def get_severity(base_dir: str, name: str) -> str:
    """Return the severity level for an env, defaulting to 'low'."""
    if not name:
        raise SeverityError("env name must not be empty")
    data = _load(base_dir)
    if name not in data:
        return "low"
    return data[name]


def remove_severity(base_dir: str, name: str) -> None:
    """Remove the severity entry for an env."""
    data = _load(base_dir)
    if name not in data:
        raise SeverityError(f"no severity entry for {name!r}")
    del data[name]
    _save(base_dir, data)


def list_severities(base_dir: str) -> dict:
    """Return all severity entries."""
    return _load(base_dir)
