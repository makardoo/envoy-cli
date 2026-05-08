"""Entropy scoring for .env file values.

Computes Shannon entropy for individual values and aggregates
an overall entropy report for an environment.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envoy_cli.storage import load_env
from envoy_cli.env_file import parse_env
from envoy_cli.crypto import decrypt


class EntropyError(Exception):
    """Raised when entropy computation fails."""


@dataclass
class EntropyReport:
    env_name: str
    scores: Dict[str, float] = field(default_factory=dict)
    average: float = 0.0
    high_entropy_keys: List[str] = field(default_factory=list)
    HIGH_THRESHOLD: float = 3.5

    def summary(self) -> str:
        lines = [f"Entropy report for '{self.env_name}' (avg={self.average:.2f})"]
        for key, score in sorted(self.scores.items(), key=lambda kv: -kv[1]):
            flag = " [HIGH]" if key in self.high_entropy_keys else ""
            lines.append(f"  {key}: {score:.3f}{flag}")
        return "\n".join(lines)


def shannon_entropy(value: str) -> float:
    """Return the Shannon entropy (bits) of *value*."""
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum(
        (c / length) * math.log2(c / length) for c in counts.values()
    )


def compute_entropy(env_name: str, passphrase: str, base_dir: Path | None = None) -> EntropyReport:
    """Decrypt *env_name* and compute per-key entropy scores."""
    if not env_name:
        raise EntropyError("env_name must not be empty")
    try:
        raw = load_env(env_name, base_dir=base_dir)
    except FileNotFoundError as exc:
        raise EntropyError(f"Environment '{env_name}' not found") from exc

    try:
        plaintext = decrypt(raw, passphrase)
    except Exception as exc:
        raise EntropyError(f"Failed to decrypt '{env_name}': {exc}") from exc

    pairs = parse_env(plaintext)
    if not pairs:
        return EntropyReport(env_name=env_name)

    scores = {key: shannon_entropy(val) for key, val in pairs.items()}
    average = sum(scores.values()) / len(scores)
    high = [k for k, v in scores.items() if v >= EntropyReport.HIGH_THRESHOLD]
    return EntropyReport(
        env_name=env_name,
        scores=scores,
        average=round(average, 4),
        high_entropy_keys=high,
    )
