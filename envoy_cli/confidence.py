"""Confidence scoring for env files based on completeness and quality signals."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class ConfidenceError(Exception):
    pass


LEVELS = ("low", "medium", "high")


def _confidence_path(base_dir: str) -> Path:
    return Path(base_dir) / "confidence.json"


def _load(base_dir: str) -> Dict[str, dict]:
    p = _confidence_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, dict]) -> None:
    p = _confidence_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_confidence(base_dir: str, name: str, level: str, note: str = "") -> None:
    """Assign a confidence level to an env."""
    if not name:
        raise ConfidenceError("env name must not be empty")
    if level not in LEVELS:
        raise ConfidenceError(f"invalid level {level!r}; choose from {LEVELS}")
    data = _load(base_dir)
    data[name] = {"level": level, "note": note}
    _save(base_dir, data)


def get_confidence(base_dir: str, name: str) -> dict:
    """Return confidence record for *name*; raises if not found."""
    data = _load(base_dir)
    if name not in data:
        raise ConfidenceError(f"no confidence record for {name!r}")
    return data[name]


def remove_confidence(base_dir: str, name: str) -> None:
    """Remove confidence record for *name*."""
    data = _load(base_dir)
    if name not in data:
        raise ConfidenceError(f"no confidence record for {name!r}")
    del data[name]
    _save(base_dir, data)


def list_confidence(base_dir: str) -> Dict[str, dict]:
    """Return all confidence records."""
    return _load(base_dir)
