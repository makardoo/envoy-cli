"""Anomaly detection for .env files — flags unusual or suspicious patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envoy_cli.storage import load_env, env_file_path
from envoy_cli.env_file import decrypt_env


class AnomalyError(Exception):
    pass


@dataclass
class AnomalyFinding:
    key: str
    reason: str
    severity: str  # "low" | "medium" | "high"


@dataclass
class AnomalyReport:
    env_name: str
    findings: List[AnomalyFinding] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.findings) == 0

    def summary(self) -> str:
        if self.clean:
            return f"{self.env_name}: no anomalies detected"
        lines = [f"{self.env_name}: {len(self.findings)} anomaly(ies) found"]
        for f in self.findings:
            lines.append(f"  [{f.severity.upper()}] {f.key}: {f.reason}")
        return "\n".join(lines)


_LONG_VALUE_THRESHOLD = 500
_HIGH_ENTROPY_THRESHOLD = 4.5
_PLACEHOLDER_RE = re.compile(r"^(CHANGE_?ME|TODO|FIXME|PLACEHOLDER|REPLACE_?ME)$", re.I)
_LOCALHOST_RE = re.compile(r"localhost|127\.0\.0\.1", re.I)


def _shannon_entropy(value: str) -> float:
    import math
    if not value:
        return 0.0
    freq = {c: value.count(c) / len(value) for c in set(value)}
    return -sum(p * math.log2(p) for p in freq.values())


def scan_content(content: str, env_name: str = "<unknown>") -> AnomalyReport:
    """Scan decrypted .env content for anomalies."""
    report = AnomalyReport(env_name=env_name)
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) > _LONG_VALUE_THRESHOLD:
            report.findings.append(AnomalyFinding(key, "value exceeds length threshold", "medium"))
        if _PLACEHOLDER_RE.match(value):
            report.findings.append(AnomalyFinding(key, "placeholder value detected", "high"))
        if _LOCALHOST_RE.search(value):
            report.findings.append(AnomalyFinding(key, "localhost reference in value", "low"))
        if len(value) >= 16 and _shannon_entropy(value) >= _HIGH_ENTROPY_THRESHOLD:
            report.findings.append(AnomalyFinding(key, "high-entropy value (possible raw secret)", "medium"))
    return report


def scan_env(env_name: str, passphrase: str, base_dir: Optional[Path] = None) -> AnomalyReport:
    """Load, decrypt, and scan a stored env for anomalies."""
    if not env_name:
        raise AnomalyError("env_name must not be empty")
    try:
        encrypted = load_env(env_name, base_dir=base_dir)
    except FileNotFoundError:
        raise AnomalyError(f"env '{env_name}' not found")
    content = decrypt_env(encrypted, passphrase)
    return scan_content(content, env_name=env_name)
