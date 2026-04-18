"""Tests for envoy_cli.ttl."""
import time
import pytest
from envoy_cli.ttl import (
    TTLError,
    set_ttl,
    get_ttl,
    is_expired,
    remove_ttl,
    list_ttls,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_ttl(base):
    set_ttl(base, "production", 3600)
    info = get_ttl(base, "production")
    assert info["seconds"] == 3600
    assert info["expires_at"] > time.time()


def test_set_creates_file(base, tmp_path):
    set_ttl(base, "staging", 60)
    assert (tmp_path / ".envoy" / "ttl.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(TTLError, match="No TTL set"):
        get_ttl(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(TTLError):
        set_ttl(base, "", 60)


def test_set_nonpositive_seconds_raises(base):
    with pytest.raises(TTLError):
        set_ttl(base, "dev", 0)
    with pytest.raises(TTLError):
        set_ttl(base, "dev", -10)


def test_is_expired_false_for_future(base):
    set_ttl(base, "dev", 9999)
    assert is_expired(base, "dev") is False


def test_is_expired_true_for_past(base):
    set_ttl(base, "dev", 1)
    import envoy_cli.ttl as ttl_mod
    original = ttl_mod.time.time
    ttl_mod.time.time = lambda: time.time() + 9999
    try:
        assert is_expired(base, "dev") is True
    finally:
        ttl_mod.time.time = original


def test_is_expired_no_ttl_returns_false(base):
    assert is_expired(base, "unknown") is False


def test_remove_ttl(base):
    set_ttl(base, "staging", 100)
    remove_ttl(base, "staging")
    with pytest.raises(TTLError):
        get_ttl(base, "staging")


def test_remove_missing_raises(base):
    with pytest.raises(TTLError):
        remove_ttl(base, "nonexistent")


def test_list_ttls(base):
    set_ttl(base, "a", 100)
    set_ttl(base, "b", 200)
    entries = list_ttls(base)
    names = {e["env_name"] for e in entries}
    assert names == {"a", "b"}
    for e in entries:
        assert "expired" in e
        assert e["expired"] is False


def test_list_ttls_empty(base):
    assert list_ttls(base) == []
