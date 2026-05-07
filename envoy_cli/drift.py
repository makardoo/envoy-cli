"""Drift detection: compare a live env file against a stored/reference env."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envoy_cli.storage import load_env
from envoy_cli.env_file import decrypt_env


class DriftError(Exception):
    """Raised when drift detection cannot complete."""


@dataclass
class DriftReport:
    env_name: str
    added: List[str] = field(default_factory=list)      # keys in live but not in stored
    removed: List[str] = field(default_factory=list)    # keys in stored but not in live
    changed: List[str] = field(default_factory=list)    # keys present in both but different values

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        if not self.has_drift:
            return f"{self.env_name}: no drift detected"
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        return f"{self.env_name}: " + ", ".join(parts)


def _parse_to_dict(content: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def detect_drift(
    env_name: str,
    live_content: str,
    passphrase: str,
    base_dir: Optional[str] = None,
) -> DriftReport:
    """Compare *live_content* (plain .env text) against the stored encrypted env."""
    if not env_name:
        raise DriftError("env_name must not be empty")

    try:
        encrypted = load_env(env_name, base_dir=base_dir)
    except FileNotFoundError:
        raise DriftError(f"No stored env found for '{env_name}'")

    stored_plain = decrypt_env(encrypted, passphrase)
    stored = _parse_to_dict(stored_plain)
    live = _parse_to_dict(live_content)

    report = DriftReport(env_name=env_name)
    all_keys = set(stored) | set(live)
    for key in sorted(all_keys):
        if key in live and key not in stored:
            report.added.append(key)
        elif key in stored and key not in live:
            report.removed.append(key)
        elif stored.get(key) != live.get(key):
            report.changed.append(key)

    return report
