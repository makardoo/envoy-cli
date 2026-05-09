"""Track and report key coverage for .env files against a reference schema."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class CoverageError(Exception):
    """Raised for coverage-related errors."""


@dataclass
class CoverageReport:
    env_name: str
    total_keys: int
    present_keys: List[str]
    missing_keys: List[str]
    extra_keys: List[str]
    score: float  # 0.0 – 1.0

    @property
    def summary(self) -> str:
        pct = int(self.score * 100)
        return (
            f"{self.env_name}: {pct}% coverage "
            f"({len(self.present_keys)}/{self.total_keys} required keys present)"
        )


def _coverage_path(base_dir: Path) -> Path:
    return base_dir / "coverage.json"


def _load(base_dir: Path) -> Dict:
    p = _coverage_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: Dict) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    _coverage_path(base_dir).write_text(json.dumps(data, indent=2))


def compute_coverage(
    env_name: str,
    content: str,
    required_keys: List[str],
    base_dir: Path,
) -> CoverageReport:
    """Compute coverage of *required_keys* in *content* and persist the result."""
    if not env_name:
        raise CoverageError("env_name must not be empty")
    if not required_keys:
        raise CoverageError("required_keys must not be empty")

    present: List[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in required_keys:
            present.append(key)

    missing = [k for k in required_keys if k not in present]
    all_keys: List[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        all_keys.append(stripped.split("=", 1)[0].strip())
    extra = [k for k in all_keys if k not in required_keys]

    total = len(required_keys)
    score = len(present) / total if total else 0.0

    report = CoverageReport(
        env_name=env_name,
        total_keys=total,
        present_keys=present,
        missing_keys=missing,
        extra_keys=extra,
        score=score,
    )

    data = _load(base_dir)
    data[env_name] = {
        "total_keys": total,
        "present_keys": present,
        "missing_keys": missing,
        "extra_keys": extra,
        "score": score,
    }
    _save(base_dir, data)
    return report


def get_coverage(env_name: str, base_dir: Path) -> CoverageReport:
    """Load a previously computed coverage report."""
    if not env_name:
        raise CoverageError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise CoverageError(f"No coverage report found for '{env_name}'")
    d = data[env_name]
    return CoverageReport(
        env_name=env_name,
        total_keys=d["total_keys"],
        present_keys=d["present_keys"],
        missing_keys=d["missing_keys"],
        extra_keys=d["extra_keys"],
        score=d["score"],
    )


def list_coverage(base_dir: Path) -> List[str]:
    """Return env names that have a stored coverage report."""
    return list(_load(base_dir).keys())
