"""Tests for envoy_cli.expiry."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from envoy_cli.expiry import (
    ExpiryError,
    get_expiry,
    is_expired,
    list_expiries,
    remove_expiry,
    set_expiry,
)


@pytest.fixture
def base(tmp_path):
    return tmp_path


def _future(days: int = 1) -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(days=days)


def _past(days: int = 1) -> datetime:
    return datetime.now(tz=timezone.utc) - timedelta(days=days)


def test_set_and_get_expiry(base):
    dt = _future(10)
    set_expiry(base, "prod", dt)
    result = get_expiry(base, "prod")
    assert result.year == dt.year
    assert result.month == dt.month
    assert result.day == dt.day


def test_set_creates_file(base):
    set_expiry(base, "staging", _future())
    assert (base / "expiry.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(ExpiryError, match="No expiry set"):
        get_expiry(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(ExpiryError):
        set_expiry(base, "", _future())


def test_remove_expiry(base):
    set_expiry(base, "dev", _future())
    remove_expiry(base, "dev")
    with pytest.raises(ExpiryError):
        get_expiry(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(ExpiryError, match="No expiry set"):
        remove_expiry(base, "nope")


def test_is_expired_future_returns_false(base):
    set_expiry(base, "prod", _future(5))
    assert is_expired(base, "prod") is False


def test_is_expired_past_returns_true(base):
    set_expiry(base, "old", _past(3))
    assert is_expired(base, "old") is True


def test_is_expired_no_entry_returns_false(base):
    assert is_expired(base, "unknown") is False


def test_list_expiries_empty(base):
    assert list_expiries(base) == {}


def test_list_expiries_returns_all(base):
    set_expiry(base, "a", _future(1))
    set_expiry(base, "b", _future(2))
    result = list_expiries(base)
    assert set(result.keys()) == {"a", "b"}
    for v in result.values():
        assert isinstance(v, datetime)


def test_overwrite_expiry(base):
    set_expiry(base, "prod", _future(10))
    set_expiry(base, "prod", _future(1))
    exp = get_expiry(base, "prod")
    # Should be close to 1 day, not 10
    from datetime import timedelta as td
    diff = exp - datetime.now(tz=timezone.utc)
    assert diff.days < 5
