"""Tests for envoy_cli.confidence."""
import pytest
from envoy_cli.confidence import (
    ConfidenceError,
    set_confidence,
    get_confidence,
    remove_confidence,
    list_confidence,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_confidence(base):
    set_confidence(base, "prod", "high")
    rec = get_confidence(base, "prod")
    assert rec["level"] == "high"
    assert rec["note"] == ""


def test_set_creates_file(base, tmp_path):
    set_confidence(base, "staging", "medium")
    assert (tmp_path / "confidence.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(ConfidenceError, match="no confidence record"):
        get_confidence(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(ConfidenceError, match="must not be empty"):
        set_confidence(base, "", "low")


def test_set_invalid_level_raises(base):
    with pytest.raises(ConfidenceError, match="invalid level"):
        set_confidence(base, "dev", "extreme")


def test_set_with_note(base):
    set_confidence(base, "dev", "low", note="needs review")
    rec = get_confidence(base, "dev")
    assert rec["note"] == "needs review"


def test_remove_confidence(base):
    set_confidence(base, "dev", "medium")
    remove_confidence(base, "dev")
    with pytest.raises(ConfidenceError):
        get_confidence(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(ConfidenceError, match="no confidence record"):
        remove_confidence(base, "ghost")


def test_list_empty(base):
    assert list_confidence(base) == {}


def test_list_returns_all(base):
    set_confidence(base, "prod", "high")
    set_confidence(base, "staging", "medium")
    records = list_confidence(base)
    assert set(records.keys()) == {"prod", "staging"}


def test_overwrite_existing(base):
    set_confidence(base, "prod", "low")
    set_confidence(base, "prod", "high", note="updated")
    rec = get_confidence(base, "prod")
    assert rec["level"] == "high"
    assert rec["note"] == "updated"
