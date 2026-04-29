"""Tests for envoy_cli.spotlight."""

from __future__ import annotations

import pytest

from envoy_cli.spotlight import (
    SpotlightError,
    spotlight_env,
    remove_spotlight,
    get_spotlight,
    list_spotlights,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_spotlight_and_get(base):
    spotlight_env(base, "prod", "critical release")
    assert get_spotlight(base, "prod") == "critical release"


def test_spotlight_creates_file(base):
    from pathlib import Path
    spotlight_env(base, "staging")
    assert (Path(base) / "spotlights.json").exists()


def test_spotlight_empty_reason(base):
    spotlight_env(base, "dev")
    assert get_spotlight(base, "dev") == ""


def test_get_missing_raises(base):
    with pytest.raises(SpotlightError, match="not spotlighted"):
        get_spotlight(base, "ghost")


def test_spotlight_empty_name_raises(base):
    with pytest.raises(SpotlightError, match="must not be empty"):
        spotlight_env(base, "")


def test_remove_spotlight(base):
    spotlight_env(base, "prod")
    remove_spotlight(base, "prod")
    with pytest.raises(SpotlightError):
        get_spotlight(base, "prod")


def test_remove_missing_raises(base):
    with pytest.raises(SpotlightError, match="not spotlighted"):
        remove_spotlight(base, "ghost")


def test_list_empty(base):
    assert list_spotlights(base) == []


def test_list_returns_entries(base):
    spotlight_env(base, "prod", "release")
    spotlight_env(base, "staging", "qa")
    entries = list_spotlights(base)
    names = [e["name"] for e in entries]
    assert "prod" in names
    assert "staging" in names


def test_overwrite_reason(base):
    spotlight_env(base, "prod", "first")
    spotlight_env(base, "prod", "updated")
    assert get_spotlight(base, "prod") == "updated"
