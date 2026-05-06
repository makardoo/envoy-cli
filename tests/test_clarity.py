"""Tests for envoy_cli.clarity."""

from __future__ import annotations

import json

import pytest

from envoy_cli.clarity import (
    ClarityError,
    VALID_LEVELS,
    get_clarity,
    list_clarity,
    remove_clarity,
    set_clarity,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_clarity(base):
    set_clarity(base, "prod", "documented", note="fully annotated")
    rec = get_clarity(base, "prod")
    assert rec["level"] == "documented"
    assert rec["note"] == "fully annotated"


def test_set_creates_file(base):
    set_clarity(base, "staging", "minimal")
    import pathlib
    assert (pathlib.Path(base) / "clarity.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(ClarityError, match="No clarity record"):
        get_clarity(base, "missing")


def test_set_empty_name_raises(base):
    with pytest.raises(ClarityError, match="must not be empty"):
        set_clarity(base, "", "opaque")


def test_set_invalid_level_raises(base):
    with pytest.raises(ClarityError, match="Invalid clarity level"):
        set_clarity(base, "dev", "superb")


def test_remove_clarity(base):
    set_clarity(base, "dev", "opaque")
    remove_clarity(base, "dev")
    with pytest.raises(ClarityError):
        get_clarity(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(ClarityError, match="No clarity record"):
        remove_clarity(base, "ghost")


def test_list_empty(base):
    assert list_clarity(base) == {}


def test_list_returns_all(base):
    set_clarity(base, "prod", "exemplary")
    set_clarity(base, "dev", "opaque")
    data = list_clarity(base)
    assert set(data.keys()) == {"prod", "dev"}


def test_valid_levels_constant():
    assert "opaque" in VALID_LEVELS
    assert "exemplary" in VALID_LEVELS
    assert len(VALID_LEVELS) == 4


def test_file_contains_valid_json(base):
    set_clarity(base, "qa", "minimal", note="needs work")
    import pathlib
    raw = (pathlib.Path(base) / "clarity.json").read_text()
    parsed = json.loads(raw)
    assert parsed["qa"]["level"] == "minimal"
