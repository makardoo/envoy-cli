"""Tests for envoy_cli.impact."""
from __future__ import annotations

import json
import pytest

from envoy_cli.impact import (
    ImpactError,
    get_impact,
    list_impact,
    remove_impact,
    set_impact,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_impact(base):
    set_impact(base, "prod", "critical")
    assert get_impact(base, "prod") == "critical"


def test_set_creates_file(base):
    set_impact(base, "staging", "medium")
    p = __import__("pathlib").Path(base) / "impact.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["staging"] == "medium"


def test_get_missing_returns_default(base):
    assert get_impact(base, "ghost") == "low"


def test_set_empty_name_raises(base):
    with pytest.raises(ImpactError, match="empty"):
        set_impact(base, "", "high")


def test_set_invalid_level_raises(base):
    with pytest.raises(ImpactError, match="invalid impact level"):
        set_impact(base, "dev", "extreme")


def test_remove_impact(base):
    set_impact(base, "dev", "low")
    remove_impact(base, "dev")
    assert get_impact(base, "dev") == "low"  # back to default


def test_remove_missing_raises(base):
    with pytest.raises(ImpactError):
        remove_impact(base, "nonexistent")


def test_list_empty(base):
    assert list_impact(base) == {}


def test_list_returns_all(base):
    set_impact(base, "prod", "critical")
    set_impact(base, "dev", "low")
    result = list_impact(base)
    assert result == {"prod": "critical", "dev": "low"}


def test_overwrite_existing(base):
    set_impact(base, "prod", "medium")
    set_impact(base, "prod", "high")
    assert get_impact(base, "prod") == "high"
