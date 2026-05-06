"""Tests for envoy_cli.deprecation."""
import pytest

from envoy_cli.deprecation import (
    DeprecationError,
    deprecate_env,
    get_deprecation,
    is_deprecated,
    list_deprecations,
    remove_deprecation,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_deprecate_and_get(base):
    entry = deprecate_env(base, "staging", reason="superseded", replacement="staging-v2")
    assert entry["reason"] == "superseded"
    assert entry["replacement"] == "staging-v2"
    assert "deprecated_at" in entry


def test_deprecate_creates_file(base):
    from pathlib import Path
    deprecate_env(base, "prod")
    assert (Path(base) / "deprecations.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(DeprecationError, match="no deprecation"):
        get_deprecation(base, "ghost")


def test_deprecate_empty_name_raises(base):
    with pytest.raises(DeprecationError, match="must not be empty"):
        deprecate_env(base, "")


def test_get_empty_name_raises(base):
    with pytest.raises(DeprecationError, match="must not be empty"):
        get_deprecation(base, "")


def test_is_deprecated_true(base):
    deprecate_env(base, "old-env")
    assert is_deprecated(base, "old-env") is True


def test_is_deprecated_false(base):
    assert is_deprecated(base, "fresh-env") is False


def test_remove_deprecation(base):
    deprecate_env(base, "staging")
    remove_deprecation(base, "staging")
    assert is_deprecated(base, "staging") is False


def test_remove_missing_raises(base):
    with pytest.raises(DeprecationError, match="no deprecation"):
        remove_deprecation(base, "nonexistent")


def test_list_deprecations_empty(base):
    assert list_deprecations(base) == []


def test_list_deprecations_returns_entries(base):
    deprecate_env(base, "alpha", reason="old")
    deprecate_env(base, "beta", replacement="beta-v2")
    results = list_deprecations(base)
    names = {r["name"] for r in results}
    assert names == {"alpha", "beta"}


def test_deprecation_no_replacement_defaults_none(base):
    deprecate_env(base, "legacy")
    entry = get_deprecation(base, "legacy")
    assert entry["replacement"] is None


def test_deprecate_overwrites_existing(base):
    deprecate_env(base, "staging", reason="first")
    deprecate_env(base, "staging", reason="second")
    entry = get_deprecation(base, "staging")
    assert entry["reason"] == "second"
