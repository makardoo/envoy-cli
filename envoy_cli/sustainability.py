"""Sustainability scoring for env files.

Tracks how 'sustainable' an env file is based on documentation,
stability, and maintenance signals.
"""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


class SustainabilityError(Exception):
    pass


@dataclass
class SustainabilityReport:
    env_name: str
    score: float          # 0.0 – 100.0
    has_comment: bool
    has_owner: bool
    has_ttl: bool
    has_schema: bool
    is_stable: bool

    def summary(self) -> str:
        grade = "A" if self.score >= 80 else "B" if self.score >= 60 else "C" if self.score >= 40 else "D"
        return f"{self.env_name}: {self.score:.1f}/100 (grade {grade})"


def _sustainability_path(base_dir: Path) -> Path:
    return base_dir / "sustainability.json"


def _load(base_dir: Path) -> dict:
    p = _sustainability_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: dict) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _sustainability_path(base_dir).write_text(json.dumps(data, indent=2))


def compute_sustainability(
    base_dir: Path,
    env_name: str,
    *,
    has_comment: bool = False,
    has_owner: bool = False,
    has_ttl: bool = False,
    has_schema: bool = False,
    is_stable: bool = False,
) -> SustainabilityReport:
    if not env_name:
        raise SustainabilityError("env_name must not be empty")

    weights = {
        "has_comment": 20.0,
        "has_owner": 25.0,
        "has_ttl": 20.0,
        "has_schema": 20.0,
        "is_stable": 15.0,
    }
    flags = {
        "has_comment": has_comment,
        "has_owner": has_owner,
        "has_ttl": has_ttl,
        "has_schema": has_schema,
        "is_stable": is_stable,
    }
    score = sum(w for k, w in weights.items() if flags[k])

    report = SustainabilityReport(
        env_name=env_name,
        score=round(score, 2),
        **flags,
    )

    data = _load(base_dir)
    data[env_name] = asdict(report)
    _save(base_dir, data)
    return report


def get_sustainability(base_dir: Path, env_name: str) -> SustainabilityReport:
    data = _load(base_dir)
    if env_name not in data:
        raise SustainabilityError(f"No sustainability record for '{env_name}'")
    return SustainabilityReport(**data[env_name])


def list_sustainability(base_dir: Path) -> list[SustainabilityReport]:
    return [SustainabilityReport(**v) for v in _load(base_dir).values()]
