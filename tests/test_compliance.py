"""Tests for envoy_cli.compliance."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.compliance import (
    ComplianceError,
    check_compliance,
    get_required_keys,
    list_policies,
    remove_policy,
    set_required_keys,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_set_and_get_required_keys(base):
    set_required_keys(base, "prod", ["DB_URL", "SECRET_KEY"])
    keys = get_required_keys(base, "prod")
    assert "DB_URL" in keys
    assert "SECRET_KEY" in keys


def test_set_creates_policy_file(base):
    set_required_keys(base, "staging", ["API_KEY"])
    assert (base / "compliance" / "policy.json").exists()


def test_get_missing_policy_raises(base):
    with pytest.raises(ComplianceError, match="No compliance policy"):
        get_required_keys(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(ComplianceError):
        set_required_keys(base, "", ["KEY"])


def test_set_deduplicates_keys(base):
    set_required_keys(base, "dev", ["KEY", "KEY", "OTHER"])
    keys = get_required_keys(base, "dev")
    assert keys.count("KEY") == 1


def test_remove_policy(base):
    set_required_keys(base, "prod", ["KEY"])
    remove_policy(base, "prod")
    with pytest.raises(ComplianceError):
        get_required_keys(base, "prod")


def test_remove_missing_raises(base):
    with pytest.raises(ComplianceError):
        remove_policy(base, "ghost")


def test_list_policies_empty(base):
    assert list_policies(base) == {}


def test_list_policies_returns_all(base):
    set_required_keys(base, "prod", ["A"])
    set_required_keys(base, "staging", ["B", "C"])
    policies = list_policies(base)
    assert "prod" in policies
    assert "staging" in policies


def test_check_compliance_passes(base):
    set_required_keys(base, "prod", ["DB_URL", "SECRET_KEY"])
    result = check_compliance(
        base, "prod", {"DB_URL": "postgres://", "SECRET_KEY": "abc123"}
    )
    assert result.passed
    assert result.violations == []


def test_check_compliance_missing_key(base):
    set_required_keys(base, "prod", ["DB_URL", "SECRET_KEY"])
    result = check_compliance(base, "prod", {"DB_URL": "postgres://"})
    assert not result.passed
    assert any(v.key == "SECRET_KEY" for v in result.violations)


def test_check_compliance_empty_value(base):
    set_required_keys(base, "prod", ["API_KEY"])
    result = check_compliance(base, "prod", {"API_KEY": "   "})
    assert not result.passed
    assert any("empty value" in v.reason for v in result.violations)


def test_check_compliance_no_policy_passes(base):
    # No policy defined means no requirements — should pass trivially
    result = check_compliance(base, "unknown", {"WHATEVER": "value"})
    assert result.passed


def test_check_compliance_multiple_violations(base):
    set_required_keys(base, "prod", ["A", "B", "C"])
    result = check_compliance(base, "prod", {})
    assert len(result.violations) == 3
