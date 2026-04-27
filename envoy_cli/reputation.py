"""Reputation scoring for env files based on historical behaviour."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ReputationError(Exception):
    pass


REPUTATION_LEVELS = ("untrusted", "low", "medium", "high", "trusted")

_SCORE_WEIGHTS: Dict[str, int] = {
    "audit_entries": 2,
    "snapshots": 3,
    "compliance_passes": 5,
    "secret_scans_clean": 4,
    "anomaly_scans_clean": 3,
}


def _reputation_path(base_dir: Path) -> Path:
    return base_dir / "reputation.json"


def _load(base_dir: Path) -> Dict[str, dict]:
    p = _reputation_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: Dict[str, dict]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _reputation_path(base_dir).write_text(json.dumps(data, indent=2))


def record_event(base_dir: Path, env_name: str, event: str) -> None:
    """Increment an event counter for *env_name*."""
    if not env_name:
        raise ReputationError("env_name must not be empty")
    if event not in _SCORE_WEIGHTS:
        raise ReputationError(f"Unknown reputation event: {event!r}")
    data = _load(base_dir)
    entry = data.setdefault(env_name, {k: 0 for k in _SCORE_WEIGHTS})
    entry[event] = entry.get(event, 0) + 1
    _save(base_dir, data)


def compute_reputation(base_dir: Path, env_name: str) -> Dict[str, object]:
    """Return a reputation dict with raw counters, score and level."""
    if not env_name:
        raise ReputationError("env_name must not be empty")
    data = _load(base_dir)
    counters: Dict[str, int] = data.get(env_name, {k: 0 for k in _SCORE_WEIGHTS})
    score = sum(counters.get(k, 0) * w for k, w in _SCORE_WEIGHTS.items())
    level = _score_to_level(score)
    return {"env_name": env_name, "counters": counters, "score": score, "level": level}


def _score_to_level(score: int) -> str:
    if score >= 80:
        return "trusted"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    if score >= 10:
        return "low"
    return "untrusted"


def list_reputations(base_dir: Path) -> List[Dict[str, object]]:
    data = _load(base_dir)
    return [compute_reputation(base_dir, name) for name in sorted(data)]


def reset_reputation(base_dir: Path, env_name: str) -> None:
    if not env_name:
        raise ReputationError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise ReputationError(f"No reputation record for {env_name!r}")
    del data[env_name]
    _save(base_dir, data)
