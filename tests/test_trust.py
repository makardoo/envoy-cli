"""Tests for envoy_cli.trust."""
from __future__ import annotations

import json

import pytest

from envoy_cli.trust import (
    TRUST_LEVELS,
    TrustError,
    get_trust,
    list_trust,
    remove_trust,
    set_trust,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_trust(base):
    set_trust(base, "prod", "high")
    assert get_trust(base, "prod") == "high"


def test_set_creates_file(base):
    set_trust(base, "staging", "medium")
    p = __import__("pathlib").Path(base) / "trust.json"
    assert p.exists()


def test_get_missing_returns_untrusted(base):
    assert get_trust(base, "unknown") == "untrusted"


def test_set_empty_name_raises(base):
    with pytest.raises(TrustError, match="must not be empty"):
        set_trust(base, "", "high")


def test_get_empty_name_raises(base):
    with pytest.raises(TrustError, match="must not be empty"):
        get_trust(base, "")


def test_set_invalid_level_raises(base):
    with pytest.raises(TrustError, match="invalid trust level"):
        set_trust(base, "dev", "super")


def test_remove_trust(base):
    set_trust(base, "dev", "low")
    remove_trust(base, "dev")
    assert get_trust(base, "dev") == "untrusted"


def test_remove_missing_raises(base):
    with pytest.raises(TrustError, match="no trust record"):
        remove_trust(base, "ghost")


def test_remove_empty_name_raises(base):
    with pytest.raises(TrustError, match="must not be empty"):
        remove_trust(base, "")


def test_list_trust_empty(base):
    assert list_trust(base) == []


def test_list_trust_returns_entries(base):
    set_trust(base, "prod", "verified")
    set_trust(base, "dev", "low")
    entries = list_trust(base)
    names = [e["name"] for e in entries]
    assert "prod" in names
    assert "dev" in names


def test_list_trust_sorted(base):
    set_trust(base, "z-env", "medium")
    set_trust(base, "a-env", "high")
    entries = list_trust(base)
    assert entries[0]["name"] == "a-env"


def test_all_trust_levels_accepted(base):
    for i, level in enumerate(TRUST_LEVELS):
        set_trust(base, f"env-{i}", level)
        assert get_trust(base, f"env-{i}") == level


def test_overwrite_trust_level(base):
    set_trust(base, "prod", "low")
    set_trust(base, "prod", "verified")
    assert get_trust(base, "prod") == "verified"


def test_persisted_as_valid_json(base):
    set_trust(base, "staging", "medium")
    import pathlib
    raw = pathlib.Path(base, "trust.json").read_text()
    data = json.loads(raw)
    assert data["staging"] == "medium"
