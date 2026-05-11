"""Tests for envoy_cli.affinity."""
from __future__ import annotations

import pytest

from envoy_cli.affinity import (
    AffinityError,
    set_affinity,
    get_affinity,
    remove_affinity,
    list_affinities,
    list_all,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_affinity(base):
    set_affinity(base, "prod", "staging", "strong")
    assert get_affinity(base, "prod", "staging") == "strong"


def test_set_creates_file(base, tmp_path):
    set_affinity(base, "prod", "dev")
    assert (tmp_path / "affinity.json").exists()


def test_set_default_strength_is_weak(base):
    set_affinity(base, "prod", "dev")
    assert get_affinity(base, "prod", "dev") == "weak"


def test_get_missing_raises(base):
    with pytest.raises(AffinityError):
        get_affinity(base, "prod", "staging")


def test_set_empty_env_name_raises(base):
    with pytest.raises(AffinityError):
        set_affinity(base, "", "staging")


def test_set_empty_related_raises(base):
    with pytest.raises(AffinityError):
        set_affinity(base, "prod", "")


def test_set_invalid_strength_raises(base):
    with pytest.raises(AffinityError, match="strength must be"):
        set_affinity(base, "prod", "staging", "ultra")


def test_remove_affinity(base):
    set_affinity(base, "prod", "staging")
    remove_affinity(base, "prod", "staging")
    with pytest.raises(AffinityError):
        get_affinity(base, "prod", "staging")


def test_remove_missing_raises(base):
    with pytest.raises(AffinityError):
        remove_affinity(base, "prod", "staging")


def test_list_affinities_returns_dict(base):
    set_affinity(base, "prod", "staging", "moderate")
    set_affinity(base, "prod", "dev", "weak")
    result = list_affinities(base, "prod")
    assert result == {"staging": "moderate", "dev": "weak"}


def test_list_affinities_empty(base):
    assert list_affinities(base, "prod") == {}


def test_list_all_returns_full_map(base):
    set_affinity(base, "prod", "staging")
    set_affinity(base, "dev", "local")
    data = list_all(base)
    assert "prod" in data
    assert "dev" in data


def test_overwrite_strength(base):
    set_affinity(base, "prod", "staging", "weak")
    set_affinity(base, "prod", "staging", "strong")
    assert get_affinity(base, "prod", "staging") == "strong"
