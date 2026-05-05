"""Tests for envoy_cli.flagging."""
import pytest
from pathlib import Path
from envoy_cli.flagging import (
    FlaggingError,
    flag_env,
    unflag_env,
    get_flag,
    list_flagged,
    _flags_path,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_flag_and_get(base):
    flag_env(base, "prod", reason="needs review")
    result = get_flag(base, "prod")
    assert result is not None
    assert result["reason"] == "needs review"
    assert result["flagged"] is True


def test_flag_creates_file(base):
    flag_env(base, "staging")
    assert _flags_path(base).exists()


def test_flag_empty_reason(base):
    flag_env(base, "dev")
    result = get_flag(base, "dev")
    assert result["reason"] == ""


def test_get_missing_returns_none(base):
    assert get_flag(base, "nonexistent") is None


def test_flag_empty_name_raises(base):
    with pytest.raises(FlaggingError):
        flag_env(base, "")


def test_unflag_removes_entry(base):
    flag_env(base, "prod")
    unflag_env(base, "prod")
    assert get_flag(base, "prod") is None


def test_unflag_not_flagged_raises(base):
    with pytest.raises(FlaggingError, match="not flagged"):
        unflag_env(base, "prod")


def test_unflag_empty_name_raises(base):
    with pytest.raises(FlaggingError):
        unflag_env(base, "")


def test_list_flagged_empty(base):
    assert list_flagged(base) == []


def test_list_flagged_returns_names(base):
    flag_env(base, "prod")
    flag_env(base, "staging")
    flagged = list_flagged(base)
    assert "prod" in flagged
    assert "staging" in flagged
    assert len(flagged) == 2


def test_flag_overwrites_existing(base):
    flag_env(base, "prod", reason="first")
    flag_env(base, "prod", reason="second")
    result = get_flag(base, "prod")
    assert result["reason"] == "second"
    assert len(list_flagged(base)) == 1
