"""Tests for envoy_cli.badge."""

import pytest
from envoy_cli.badge import (
    BadgeError,
    set_badge,
    get_badge,
    remove_badge,
    list_badges,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_badge(base):
    set_badge(base, "prod", "stable")
    assert get_badge(base, "prod") == "stable"


def test_set_creates_file(base):
    from pathlib import Path
    set_badge(base, "staging", "wip")
    assert (Path(base) / "badges.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(BadgeError, match="No badge"):
        get_badge(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(BadgeError, match="must not be empty"):
        set_badge(base, "", "stable")


def test_set_invalid_badge_raises(base):
    with pytest.raises(BadgeError, match="Invalid badge"):
        set_badge(base, "prod", "unknown-badge")


def test_remove_badge(base):
    set_badge(base, "dev", "experimental")
    remove_badge(base, "dev")
    with pytest.raises(BadgeError):
        get_badge(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(BadgeError, match="No badge"):
        remove_badge(base, "ghost")


def test_list_badges_empty(base):
    assert list_badges(base) == {}


def test_list_badges_multiple(base):
    set_badge(base, "prod", "stable")
    set_badge(base, "staging", "wip")
    result = list_badges(base)
    assert result["prod"] == "stable"
    assert result["staging"] == "wip"


def test_overwrite_badge(base):
    set_badge(base, "prod", "stable")
    set_badge(base, "prod", "deprecated")
    assert get_badge(base, "prod") == "deprecated"
