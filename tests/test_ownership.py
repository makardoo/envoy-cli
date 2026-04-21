"""Tests for envoy_cli.ownership."""
from __future__ import annotations

import pytest

from envoy_cli.ownership import (
    OwnershipError,
    get_owner,
    list_owned,
    remove_owner,
    set_owner,
)


@pytest.fixture()
def base(tmp_path):
    return tmp_path


def test_set_and_get_owner(base):
    set_owner(base, "production", "alice")
    info = get_owner(base, "production")
    assert info["owner"] == "alice"
    assert info["team"] is None


def test_set_with_team(base):
    set_owner(base, "staging", "bob", team="backend")
    info = get_owner(base, "staging")
    assert info["owner"] == "bob"
    assert info["team"] == "backend"


def test_set_creates_file(base):
    set_owner(base, "dev", "carol")
    assert (base / "ownership.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(OwnershipError, match="No ownership record"):
        get_owner(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(OwnershipError):
        set_owner(base, "", "alice")


def test_set_empty_owner_raises(base):
    with pytest.raises(OwnershipError):
        set_owner(base, "production", "")


def test_remove_owner(base):
    set_owner(base, "production", "alice")
    remove_owner(base, "production")
    with pytest.raises(OwnershipError):
        get_owner(base, "production")


def test_remove_missing_raises(base):
    with pytest.raises(OwnershipError, match="No ownership record"):
        remove_owner(base, "ghost")


def test_list_owned_all(base):
    set_owner(base, "prod", "alice", team="ops")
    set_owner(base, "staging", "bob", team="dev")
    assert sorted(list_owned(base)) == ["prod", "staging"]


def test_list_owned_filter_by_owner(base):
    set_owner(base, "prod", "alice")
    set_owner(base, "staging", "bob")
    assert list_owned(base, owner="alice") == ["prod"]


def test_list_owned_filter_by_team(base):
    set_owner(base, "prod", "alice", team="ops")
    set_owner(base, "staging", "bob", team="dev")
    assert list_owned(base, team="ops") == ["prod"]


def test_list_owned_empty(base):
    assert list_owned(base) == []


def test_overwrite_owner(base):
    set_owner(base, "prod", "alice")
    set_owner(base, "prod", "dave", team="platform")
    info = get_owner(base, "prod")
    assert info["owner"] == "dave"
    assert info["team"] == "platform"
