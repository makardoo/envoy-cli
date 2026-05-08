"""Coherence scoring for env files — measures how internally consistent
a set of variables is (naming conventions, prefix consistency, etc.)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


class CoherenceError(Exception):
    pass


def _coherence_path(base_dir: str) -> Path:
    return Path(base_dir) / "coherence.json"


def _load(base_dir: str) -> dict:
    p = _coherence_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _coherence_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


@dataclass
class CoherenceReport:
    env_name: str
    score: float  # 0.0 – 1.0
    total_keys: int
    issues: list[str] = field(default_factory=list)

    @property
    def coherent(self) -> bool:
        return self.score >= 0.8

    def summary(self) -> str:
        status = "coherent" if self.coherent else "incoherent"
        return f"{self.env_name}: {self.score:.2f} ({status}), {len(self.issues)} issue(s)"


def compute_coherence(env_name: str, content: str, base_dir: str) -> CoherenceReport:
    if not env_name.strip():
        raise CoherenceError("env_name must not be empty")

    lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    keys = []
    issues = []

    for line in lines:
        if "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        keys.append(key)

    if not keys:
        report = CoherenceReport(env_name=env_name, score=0.0, total_keys=0, issues=["no keys found"])
        _persist(base_dir, env_name, report)
        return report

    # Check UPPER_SNAKE_CASE convention
    bad_case = [k for k in keys if not re.match(r'^[A-Z][A-Z0-9_]*$', k)]
    if bad_case:
        issues.append(f"{len(bad_case)} key(s) not UPPER_SNAKE_CASE: {bad_case[:3]}")

    # Check prefix consistency
    prefixes = [k.split("_")[0] for k in keys if "_" in k]
    if prefixes:
        most_common = max(set(prefixes), key=prefixes.count)
        outliers = [k for k in keys if "_" in k and not k.startswith(most_common + "_")]
        if len(outliers) > len(keys) * 0.3:
            issues.append(f"inconsistent prefixes detected (dominant: {most_common})")

    penalty = len(issues) * 0.15
    score = max(0.0, round(1.0 - penalty, 2))
    report = CoherenceReport(env_name=env_name, score=score, total_keys=len(keys), issues=issues)
    _persist(base_dir, env_name, report)
    return report


def _persist(base_dir: str, env_name: str, report: CoherenceReport) -> None:
    data = _load(base_dir)
    data[env_name] = {"score": report.score, "total_keys": report.total_keys, "issues": report.issues}
    _save(base_dir, data)


def get_coherence(env_name: str, base_dir: str) -> CoherenceReport:
    if not env_name.strip():
        raise CoherenceError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise CoherenceError(f"no coherence record for '{env_name}'")
    entry = data[env_name]
    return CoherenceReport(
        env_name=env_name,
        score=entry["score"],
        total_keys=entry["total_keys"],
        issues=entry["issues"],
    )


def list_coherence(base_dir: str) -> list[CoherenceReport]:
    data = _load(base_dir)
    return [
        CoherenceReport(env_name=n, score=e["score"], total_keys=e["total_keys"], issues=e["issues"])
        for n, e in data.items()
    ]
