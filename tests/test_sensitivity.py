"""Tests for envoy_cli.sensitivity."""

from __future__ import annotations

import pytest

from envoy_cli.sensitivity import (
    SensitivityError,
    get_sensitivity,
    get_sensitivity_default,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_sensitivity(base):
    set_sensitivity(base, "prod", "secret")
    assert get_sensitivity(base, "prod") == "secret"


def test_set_creates_file(base, tmp_path):
    set_sensitivity(base, "staging", "confidential")
    assert (tmp_path / "sensitivity.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(SensitivityError, match="No sensitivity level"):
        get_sensitivity(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(SensitivityError, match="must not be empty"):
        set_sensitivity(base, "", "public")


def test_set_invalid_level_raises(base):
    with pytest.raises(SensitivityError, match="Invalid level"):
        set_sensitivity(base, "dev", "ultra-secret")


def test_overwrite_existing(base):
    set_sensitivity(base, "prod", "internal")
    set_sensitivity(base, "prod", "secret")
    assert get_sensitivity(base, "prod") == "secret"


def test_remove_sensitivity(base):
    set_sensitivity(base, "dev", "public")
    remove_sensitivity(base, "dev")
    with pytest.raises(SensitivityError):
        get_sensitivity(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(SensitivityError, match="No sensitivity level"):
        remove_sensitivity(base, "ghost")


def test_list_empty(base):
    assert list_sensitivity(base) == []


def test_list_returns_sorted_entries(base):
    set_sensitivity(base, "staging", "internal")
    set_sensitivity(base, "prod", "secret")
    entries = list_sensitivity(base)
    assert len(entries) == 2
    assert entries[0]["env"] == "prod"
    assert entries[1]["env"] == "staging"


def test_get_sensitivity_default_returns_value(base):
    set_sensitivity(base, "prod", "confidential")
    assert get_sensitivity_default(base, "prod") == "confidential"


def test_get_sensitivity_default_returns_default_when_missing(base):
    assert get_sensitivity_default(base, "missing") == "internal"
    assert get_sensitivity_default(base, "missing", default="public") == "public"


def test_all_valid_levels(base):
    for level in ("public", "internal", "confidential", "secret"):
        set_sensitivity(base, f"env_{level}", level)
        assert get_sensitivity(base, f"env_{level}") == level
