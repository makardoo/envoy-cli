"""Potency module: measures and records the 'strength' of an env file.

Potency is a composite score (0–100) reflecting how well-populated and
non-trivial an env file is.  It rewards:
  - A high ratio of non-empty values
  - Values with meaningful length (> 4 chars)
  - Absence of obvious placeholder strings (e.g. 'changeme', 'todo', 'xxx')
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class PotencyError(Exception:
    """Raised when a potency operation fails."""


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

_PLACEHOLDER_RE = re.compile(
    r"^(changeme|todo|fixme|xxx+|your[_-]?.*|example|placeholder|insert[_-]?.*)$",
    re.IGNORECASE,
)


def _potency_path(base_dir: Path) -> Path:
    return base_dir / "potency.json"


def _load(base_dir: Path) -> Dict[str, dict]:
    p = _potency_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: Dict[str, dict]) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _potency_path(base_dir).write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class PotencyReport:
    env_name: str
    score: float                          # 0–100
    total_keys: int
    non_empty: int
    meaningful: int                       # len(value) > 4
    placeholder_count: int
    details: List[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"{self.env_name}: potency={self.score:.1f}/100 "
            f"(keys={self.total_keys}, non_empty={self.non_empty}, "
            f"meaningful={self.meaningful}, placeholders={self.placeholder_count})"
        )


def compute_potency(env_name: str, content: str, base_dir: Path) -> PotencyReport:
    """Compute and persist a potency report for *env_name*.

    Args:
        env_name: Logical name of the environment.
        content:  Raw .env file text.
        base_dir: Directory where ``potency.json`` is stored.

    Returns:
        A :class:`PotencyReport` instance.
    """
    if not env_name:
        raise PotencyError("env_name must not be empty")

    total = non_empty = meaningful = placeholders = 0
    details: List[str] = []

    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        total += 1
        if value:
            non_empty += 1
        if len(value) > 4:
            meaningful += 1
        if value and _PLACEHOLDER_RE.match(value):
            placeholders += 1
            details.append(f"{key}: placeholder value detected")

    if total == 0:
        score = 0.0
    else:
        fill_ratio = non_empty / total
        meaningful_ratio = meaningful / total
        placeholder_penalty = placeholders / total
        raw_score = (fill_ratio * 50) + (meaningful_ratio * 50) - (placeholder_penalty * 30)
        score = max(0.0, min(100.0, raw_score * 100 / 100))  # already in 0-100 range
        # Normalise: raw_score is already 0-100 effectively; clamp.
        score = round(max(0.0, min(100.0, raw_score)), 2)

    report = PotencyReport(
        env_name=env_name,
        score=score,
        total_keys=total,
        non_empty=non_empty,
        meaningful=meaningful,
        placeholder_count=placeholders,
        details=details,
    )

    data = _load(base_dir)
    data[env_name] = {
        "score": report.score,
        "total_keys": report.total_keys,
        "non_empty": report.non_empty,
        "meaningful": report.meaningful,
        "placeholder_count": report.placeholder_count,
    }
    _save(base_dir, data)

    return report


def get_potency(env_name: str, base_dir: Path) -> dict:
    """Return the persisted potency data for *env_name*.

    Raises:
        PotencyError: If no record exists.
    """
    if not env_name:
        raise PotencyError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise PotencyError(f"No potency record for '{env_name}'")
    return data[env_name]


def list_potency(base_dir: Path) -> Dict[str, dict]:
    """Return all persisted potency records."""
    return _load(base_dir)
