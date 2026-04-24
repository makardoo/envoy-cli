"""Environment health check module for envoy-cli."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envoy_cli.storage import get_env_dir


class HealthError(Exception):
    pass


@dataclass
class HealthIssue:
    code: str
    message: str
    severity: str  # "error" | "warning" | "info"


@dataclass
class HealthReport:
    env_name: str
    issues: List[HealthIssue] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def summary(self) -> str:
        if not self.issues:
            return f"{self.env_name}: OK"
        counts = {"error": 0, "warning": 0, "info": 0}
        for issue in self.issues:
            counts[issue.severity] += 1
        parts = [f"{v} {k}(s)" for k, v in counts.items() if v]
        return f"{self.env_name}: {', '.join(parts)}"


def _health_path(base_dir: Path) -> Path:
    return base_dir / ".envoy" / "health.json"


def _load(base_dir: Path) -> dict:
    p = _health_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: Path, data: dict) -> None:
    p = _health_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_health_rule(base_dir: Path, env_name: str, rule: str, value) -> None:
    """Set a health rule for an environment (e.g. min_keys, required_keys)."""
    if not env_name:
        raise HealthError("env_name must not be empty")
    data = _load(base_dir)
    env_rules = data.setdefault(env_name, {})
    env_rules[rule] = value
    _save(base_dir, data)


def get_health_rules(base_dir: Path, env_name: str) -> dict:
    data = _load(base_dir)
    if env_name not in data:
        raise HealthError(f"No health rules found for '{env_name}'")
    return data[env_name]


def check_health(base_dir: Path, env_name: str, content: str) -> HealthReport:
    """Run health checks on env content against configured rules."""
    report = HealthReport(env_name=env_name)
    data = _load(base_dir)
    rules = data.get(env_name, {})

    lines = [l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
    pairs = {}
    for line in lines:
        if "=" in line:
            k, _, v = line.partition("=")
            pairs[k.strip()] = v.strip()

    if "min_keys" in rules and len(pairs) < rules["min_keys"]:
        report.issues.append(HealthIssue(
            code="MIN_KEYS",
            message=f"Expected at least {rules['min_keys']} keys, found {len(pairs)}",
            severity="error",
        ))

    if "required_keys" in rules:
        for key in rules["required_keys"]:
            if key not in pairs:
                report.issues.append(HealthIssue(
                    code="MISSING_KEY",
                    message=f"Required key '{key}' is missing",
                    severity="error",
                ))

    if "warn_empty_values" in rules and rules["warn_empty_values"]:
        for k, v in pairs.items():
            if not v:
                report.issues.append(HealthIssue(
                    code="EMPTY_VALUE",
                    message=f"Key '{k}' has an empty value",
                    severity="warning",
                ))

    return report
