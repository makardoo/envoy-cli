"""Complexity scoring for .env files based on key count, value length, and structure."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class ComplexityError(Exception):
    pass


def _complexity_path(base_dir: str) -> Path:
    return Path(base_dir) / "complexity.json"


def _load(base_dir: str) -> Dict:
    p = _complexity_path(base_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save(base_dir: str, data: Dict) -> None:
    p = _complexity_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)


@dataclass
class ComplexityReport:
    env_name: str
    key_count: int
    avg_value_length: float
    long_value_count: int
    score: int
    level: str


LEVELS = [
    (0, 20, "low"),
    (21, 50, "medium"),
    (51, 100, "high"),
]


def _level(score: int) -> str:
    for lo, hi, label in LEVELS:
        if lo <= score <= hi:
            return label
    return "high"


def compute_complexity(env_name: str, content: str) -> ComplexityReport:
    if not env_name.strip():
        raise ComplexityError("env_name must not be empty")
    lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    key_count = len(lines)
    values = []
    for line in lines:
        if "=" in line:
            values.append(line.split("=", 1)[1])
    avg_len = sum(len(v) for v in values) / len(values) if values else 0.0
    long_value_count = sum(1 for v in values if len(v) > 50)
    score = min(100, key_count * 2 + int(avg_len / 5) + long_value_count * 3)
    return ComplexityReport(
        env_name=env_name,
        key_count=key_count,
        avg_value_length=round(avg_len, 2),
        long_value_count=long_value_count,
        score=score,
        level=_level(score),
    )


def record_complexity(base_dir: str, report: ComplexityReport) -> ComplexityReport:
    data = _load(base_dir)
    data[report.env_name] = {
        "key_count": report.key_count,
        "avg_value_length": report.avg_value_length,
        "long_value_count": report.long_value_count,
        "score": report.score,
        "level": report.level,
    }
    _save(base_dir, data)
    return report


def get_complexity(base_dir: str, env_name: str) -> ComplexityReport:
    data = _load(base_dir)
    if env_name not in data:
        raise ComplexityError(f"No complexity record for '{env_name}'")
    d = data[env_name]
    return ComplexityReport(env_name=env_name, **d)


def list_complexity(base_dir: str) -> List[ComplexityReport]:
    data = _load(base_dir)
    return [ComplexityReport(env_name=k, **v) for k, v in data.items()]
