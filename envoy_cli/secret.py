"""Secret detection: scan env files for potentially exposed secrets."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envoy_cli.storage import load_env
from envoy_cli.env_file import decrypt_env


class SecretError(Exception):
    pass


# Patterns that suggest a value might be a raw secret
_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("high-entropy", re.compile(r"[A-Za-z0-9+/]{32,}"))  ,
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private-key-header", re.compile(r"-----BEGIN .* PRIVATE KEY-----")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("generic-secret", re.compile(r"(?i)(secret|password|passwd|token|api[_-]?key)[^=]*=[\s]*[^\s]{8,}")),
]

_SAFE_KEYS = frozenset({"PATH", "HOME", "USER", "SHELL", "TERM", "LANG", "LC_ALL"})


@dataclass
class SecretFinding:
    key: str
    value: str
    rule: str
    line: int

    def masked_value(self) -> str:
        if len(self.value) <= 4:
            return "****"
        return self.value[:2] + "****" + self.value[-2:]


@dataclass
class ScanResult:
    env_name: str
    findings: List[SecretFinding] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.findings) == 0


def scan_content(content: str, env_name: str = "<unknown>") -> ScanResult:
    """Scan raw env content (decrypted) for secret patterns."""
    result = ScanResult(env_name=env_name)
    for lineno, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        if key in _SAFE_KEYS:
            continue
        for rule_name, pattern in _PATTERNS:
            if pattern.search(value) or pattern.search(stripped):
                result.findings.append(
                    SecretFinding(key=key, value=value, rule=rule_name, line=lineno)
                )
                break
    return result


def scan_env(env_name: str, passphrase: str, base_dir: Optional[Path] = None) -> ScanResult:
    """Load, decrypt, and scan a stored env for secrets."""
    try:
        encrypted = load_env(env_name, base_dir=base_dir)
    except FileNotFoundError:
        raise SecretError(f"env '{env_name}' not found")
    content = decrypt_env(encrypted, passphrase)
    return scan_content(content, env_name=env_name)
