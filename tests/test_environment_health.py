"""Tests for envoy_cli.environment_health."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.environment_health import (
    HealthError,
    HealthIssue,
    HealthReport,
    check_health,
    get_health_rules,
    set_health_rule,
)


@pytest.fixture
def base(tmp_path):
    return tmp_path


# --- set_health_rule / get_health_rules ---

def test_set_and_get_rule(base):
    set_health_rule(base, "prod", "min_keys", 3)
    rules = get_health_rules(base, "prod")
    assert rules["min_keys"] == 3


def test_set_creates_file(base):
    set_health_rule(base, "staging", "warn_empty_values", True)
    assert (base / ".envoy" / "health.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(HealthError, match="No health rules"):
        get_health_rules(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(HealthError):
        set_health_rule(base, "", "min_keys", 1)


def test_multiple_rules_stored_independently(base):
    set_health_rule(base, "prod", "min_keys", 5)
    set_health_rule(base, "dev", "min_keys", 1)
    assert get_health_rules(base, "prod")["min_keys"] == 5
    assert get_health_rules(base, "dev")["min_keys"] == 1


# --- check_health ---

SAMPLE_CONTENT = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"


def test_check_health_no_rules_returns_empty_issues(base):
    report = check_health(base, "prod", SAMPLE_CONTENT)
    assert report.healthy
    assert report.issues == []


def test_check_health_min_keys_pass(base):
    set_health_rule(base, "prod", "min_keys", 2)
    report = check_health(base, "prod", SAMPLE_CONTENT)
    assert report.healthy


def test_check_health_min_keys_fail(base):
    set_health_rule(base, "prod", "min_keys", 10)
    report = check_health(base, "prod", SAMPLE_CONTENT)
    assert not report.healthy
    codes = [i.code for i in report.issues]
    assert "MIN_KEYS" in codes


def test_check_health_required_keys_pass(base):
    set_health_rule(base, "prod", "required_keys", ["DB_HOST", "SECRET_KEY"])
    report = check_health(base, "prod", SAMPLE_CONTENT)
    assert report.healthy


def test_check_health_required_keys_missing(base):
    set_health_rule(base, "prod", "required_keys", ["DB_HOST", "MISSING_KEY"])
    report = check_health(base, "prod", SAMPLE_CONTENT)
    assert not report.healthy
    missing = [i for i in report.issues if i.code == "MISSING_KEY"]
    assert len(missing) == 1
    assert "MISSING_KEY" in missing[0].message


def test_check_health_warn_empty_values(base):
    content = "KEY1=value\nKEY2=\n"
    set_health_rule(base, "dev", "warn_empty_values", True)
    report = check_health(base, "dev", content)
    assert report.healthy  # warnings don't make unhealthy
    warnings = [i for i in report.issues if i.code == "EMPTY_VALUE"]
    assert len(warnings) == 1


def test_check_health_ignores_comments(base):
    content = "# comment\nKEY=val\n"
    set_health_rule(base, "prod", "min_keys", 1)
    report = check_health(base, "prod", content)
    assert report.healthy


# --- HealthReport ---

def test_health_report_summary_ok():
    r = HealthReport(env_name="prod")
    assert "OK" in r.summary


def test_health_report_summary_with_issues():
    r = HealthReport(env_name="prod", issues=[
        HealthIssue(code="X", message="msg", severity="error"),
        HealthIssue(code="Y", message="msg", severity="warning"),
    ])
    assert "error" in r.summary
    assert "warning" in r.summary
