"""Tests for envoy_cli.severity."""
from __future__ import annotations

import json

import pytest

from envoy_cli.severity import (
    SeverityError,
    get_severity,
    list_severities,
    remove_severity,
    set_severity,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_severity(base):
    set_severity(base, "prod", "high")
    assert get_severity(base, "prod") == "high"


def test_set_creates_file(base):
    set_severity(base, "staging", "medium")
    p = __import__("pathlib").Path(base) / "severity.json"
    assert p.exists()


def test_get_missing_returns_default(base):
    assert get_severity(base, "unknown") == "low"


def test_set_empty_name_raises(base):
    with pytest.raises(SeverityError, match="empty"):
        set_severity(base, "", "high")


def test_get_empty_name_raises(base):
    with pytest.raises(SeverityError, match="empty"):
        get_severity(base, "")


def test_set_invalid_level_raises(base):
    with pytest.raises(SeverityError, match="invalid severity level"):
        set_severity(base, "dev", "extreme")


def test_remove_severity(base):
    set_severity(base, "dev", "low")
    remove_severity(base, "dev")
    assert get_severity(base, "dev") == "low"  # falls back to default


def test_remove_missing_raises(base):
    with pytest.raises(SeverityError, match="no severity entry"):
        remove_severity(base, "nonexistent")


def test_list_severities_empty(base):
    assert list_severities(base) == {}


def test_list_severities_returns_all(base):
    set_severity(base, "prod", "critical")
    set_severity(base, "staging", "medium")
    result = list_severities(base)
    assert result == {"prod": "critical", "staging": "medium"}


def test_overwrite_severity(base):
    set_severity(base, "prod", "low")
    set_severity(base, "prod", "critical")
    assert get_severity(base, "prod") == "critical"


def test_all_valid_levels_accepted(base):
    for level in ("low", "medium", "high", "critical"):
        set_severity(base, f"env_{level}", level)
        assert get_severity(base, f"env_{level}") == level
