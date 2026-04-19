"""Tests for envoy_cli.retention."""
import pytest
from datetime import datetime, timedelta
from envoy_cli.retention import (
    RetentionError,
    set_retention,
    get_retention,
    remove_retention,
    list_retention,
    is_expired,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_retention(base):
    set_retention(base, "prod", 30)
    entry = get_retention(base, "prod")
    assert entry["days"] == 30
    assert "set_at" in entry


def test_set_creates_file(base, tmp_path):
    set_retention(base, "staging", 7)
    assert (tmp_path / "retention.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(RetentionError, match="No retention policy"):
        get_retention(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(RetentionError, match="env_name"):
        set_retention(base, "", 10)


def test_set_zero_days_raises(base):
    with pytest.raises(RetentionError, match="days"):
        set_retention(base, "prod", 0)


def test_set_negative_days_raises(base):
    with pytest.raises(RetentionError, match="days"):
        set_retention(base, "prod", -5)


def test_remove_retention(base):
    set_retention(base, "dev", 14)
    remove_retention(base, "dev")
    with pytest.raises(RetentionError):
        get_retention(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(RetentionError, match="No retention policy"):
        remove_retention(base, "ghost")


def test_list_retention(base):
    set_retention(base, "prod", 30)
    set_retention(base, "staging", 7)
    entries = list_retention(base)
    names = [e["env_name"] for e in entries]
    assert "prod" in names
    assert "staging" in names


def test_list_empty(base):
    assert list_retention(base) == []


def test_is_expired_false(base):
    set_retention(base, "prod", 30)
    assert not is_expired(base, "prod")


def test_is_expired_true(base):
    set_retention(base, "prod", 1)
    future = datetime.utcnow() + timedelta(days=2)
    assert is_expired(base, "prod", reference=future)
