"""Tests for envoy_cli.risk."""

from __future__ import annotations

import pytest

from envoy_cli.risk import (
    RiskError,
    set_risk,
    get_risk,
    remove_risk,
    list_risks,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_risk(base):
    set_risk(base, "prod", "high", note="handles payments")
    info = get_risk(base, "prod")
    assert info["level"] == "high"
    assert info["note"] == "handles payments"


def test_set_creates_file(base, tmp_path):
    set_risk(base, "staging", "medium")
    assert (tmp_path / "risk.json").exists()


def test_get_missing_returns_default(base):
    info = get_risk(base, "nonexistent")
    assert info["level"] == "low"
    assert info["note"] == ""


def test_set_empty_name_raises(base):
    with pytest.raises(RiskError, match="must not be empty"):
        set_risk(base, "", "low")


def test_set_invalid_level_raises(base):
    with pytest.raises(RiskError, match="invalid risk level"):
        set_risk(base, "dev", "extreme")


def test_remove_risk(base):
    set_risk(base, "dev", "low")
    remove_risk(base, "dev")
    info = get_risk(base, "dev")
    assert info["level"] == "low"  # falls back to default


def test_remove_missing_raises(base):
    with pytest.raises(RiskError, match="no risk record"):
        remove_risk(base, "ghost")


def test_list_risks_empty(base):
    assert list_risks(base) == {}


def test_list_risks_returns_all(base):
    set_risk(base, "prod", "critical")
    set_risk(base, "dev", "low")
    records = list_risks(base)
    assert set(records.keys()) == {"prod", "dev"}
    assert records["prod"]["level"] == "critical"


def test_overwrite_risk(base):
    set_risk(base, "prod", "low")
    set_risk(base, "prod", "critical", note="updated")
    info = get_risk(base, "prod")
    assert info["level"] == "critical"
    assert info["note"] == "updated"
