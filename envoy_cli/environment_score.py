"""Environment scoring: compute a health/quality score for a stored env."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envoy_cli.storage import get_env_dir, load_env
from envoy_cli.env_file import decrypt_env


class ScoreError(Exception):
    """Raised when scoring fails."""


SCORE_FILE = "scores.json"


def _scores_path(base_dir: Path) -> Path:
    return base_dir / SCORE_FILE


def _load(base_dir: Path) -> dict[str, Any]:
    p = _scores_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: dict[str, Any]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _scores_path(base_dir).write_text(json.dumps(data, indent=2))


def compute_score(env_name: str, passphrase: str, base_dir: Path | None = None) -> int:
    """Decrypt *env_name* and return an integer quality score 0-100.

    Scoring criteria (each worth points):
      - Has at least 1 key          : +20
      - No empty values             : +20
      - No duplicate keys           : +20
      - All keys are UPPER_SNAKE    : +20
      - No keys longer than 64 chars: +20
    """
    if not env_name:
        raise ScoreError("env_name must not be empty")

    base = base_dir or get_env_dir()
    try:
        raw = load_env(env_name, base_dir=base)
    except FileNotFoundError:
        raise ScoreError(f"env '{env_name}' not found")

    content = decrypt_env(raw, passphrase)
    lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    pairs = []
    for line in lines:
        if "=" in line:
            k, _, v = line.partition("=")
            pairs.append((k.strip(), v.strip()))

    score = 0
    if pairs:
        score += 20
    if pairs and all(v for _, v in pairs):
        score += 20
    keys = [k for k, _ in pairs]
    if keys and len(keys) == len(set(keys)):
        score += 20
    if keys and all(k == k.upper() and k.replace("_", "").isalnum() for k in keys):
        score += 20
    if keys and all(len(k) <= 64 for k in keys):
        score += 20

    return score


def record_score(env_name: str, score: int, base_dir: Path | None = None) -> dict[str, Any]:
    """Persist *score* for *env_name* and return the stored record."""
    base = base_dir or get_env_dir()
    data = _load(base)
    data[env_name] = {"env": env_name, "score": score}
    _save(base, data)
    return data[env_name]


def get_score(env_name: str, base_dir: Path | None = None) -> dict[str, Any]:
    """Return the last recorded score record for *env_name*."""
    base = base_dir or get_env_dir()
    data = _load(base)
    if env_name not in data:
        raise ScoreError(f"no score recorded for '{env_name}'")
    return data[env_name]


def list_scores(base_dir: Path | None = None) -> list[dict[str, Any]]:
    """Return all recorded score records sorted by env name."""
    base = base_dir or get_env_dir()
    return sorted(_load(base).values(), key=lambda r: r["env"])
