"""Alignment: track how well an env file conforms to a reference/template env."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class AlignmentError(Exception):
    """Raised when an alignment operation fails."""


def _alignment_path(base_dir: str) -> Path:
    return Path(base_dir) / "alignment.json"


def _load(base_dir: str) -> Dict[str, dict]:
    p = _alignment_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, dict]) -> None:
    p = _alignment_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def compute_alignment(
    base_dir: str,
    env_name: str,
    env_content: str,
    reference_content: str,
) -> "AlignmentReport":
    """Compare *env_content* against *reference_content* and persist the result."""
    if not env_name:
        raise AlignmentError("env_name must not be empty")

    ref_keys = _parse_keys(reference_content)
    env_keys = _parse_keys(env_content)

    missing = sorted(ref_keys - env_keys)
    extra = sorted(env_keys - ref_keys)
    matched = sorted(ref_keys & env_keys)
    total = len(ref_keys)
    score = round(len(matched) / total * 100, 2) if total else 0.0

    report = AlignmentReport(
        env_name=env_name,
        score=score,
        matched=matched,
        missing=missing,
        extra=extra,
    )

    data = _load(base_dir)
    data[env_name] = report.to_dict()
    _save(base_dir, data)
    return report


def get_alignment(base_dir: str, env_name: str) -> "AlignmentReport":
    data = _load(base_dir)
    if env_name not in data:
        raise AlignmentError(f"No alignment report found for '{env_name}'")
    return AlignmentReport(**data[env_name])


def list_alignments(base_dir: str) -> List[str]:
    return sorted(_load(base_dir).keys())


def _parse_keys(content: str) -> set:
    keys = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            keys.add(line.split("=", 1)[0].strip())
    return keys


class AlignmentReport:
    def __init__(
        self,
        env_name: str,
        score: float,
        matched: List[str],
        missing: List[str],
        extra: List[str],
    ) -> None:
        self.env_name = env_name
        self.score = score
        self.matched = matched
        self.missing = missing
        self.extra = extra

    def to_dict(self) -> dict:
        return {
            "env_name": self.env_name,
            "score": self.score,
            "matched": self.matched,
            "missing": self.missing,
            "extra": self.extra,
        }

    @property
    def is_aligned(self) -> bool:
        return self.score == 100.0
