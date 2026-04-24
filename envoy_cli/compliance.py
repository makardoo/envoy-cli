"""Compliance checking for env files against required key policies."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class ComplianceError(Exception):
    pass


@dataclass
class ComplianceViolation:
    env_name: str
    key: str
    reason: str


@dataclass
class ComplianceResult:
    env_name: str
    violations: List[ComplianceViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0


def _policy_path(base_dir: Path) -> Path:
    return base_dir / "compliance" / "policy.json"


def _load_policy(base_dir: Path) -> Dict:
    p = _policy_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policy(base_dir: Path, policy: Dict) -> None:
    p = _policy_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(policy, indent=2))


def set_required_keys(base_dir: Path, env_name: str, keys: List[str]) -> None:
    if not env_name:
        raise ComplianceError("env_name must not be empty")
    policy = _load_policy(base_dir)
    policy[env_name] = sorted(set(keys))
    _save_policy(base_dir, policy)


def get_required_keys(base_dir: Path, env_name: str) -> List[str]:
    policy = _load_policy(base_dir)
    if env_name not in policy:
        raise ComplianceError(f"No compliance policy for '{env_name}'")
    return policy[env_name]


def remove_policy(base_dir: Path, env_name: str) -> None:
    policy = _load_policy(base_dir)
    if env_name not in policy:
        raise ComplianceError(f"No compliance policy for '{env_name}'")
    del policy[env_name]
    _save_policy(base_dir, policy)


def list_policies(base_dir: Path) -> Dict[str, List[str]]:
    return _load_policy(base_dir)


def check_compliance(
    base_dir: Path, env_name: str, env_dict: Dict[str, str]
) -> ComplianceResult:
    """Check env_dict against the stored policy for env_name."""
    result = ComplianceResult(env_name=env_name)
    policy = _load_policy(base_dir)
    required = policy.get(env_name, [])
    for key in required:
        if key not in env_dict:
            result.violations.append(
                ComplianceViolation(
                    env_name=env_name,
                    key=key,
                    reason=f"Required key '{key}' is missing",
                )
            )
        elif not env_dict[key].strip():
            result.violations.append(
                ComplianceViolation(
                    env_name=env_name,
                    key=key,
                    reason=f"Required key '{key}' has an empty value",
                )
            )
    return result
