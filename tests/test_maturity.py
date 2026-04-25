"""Tests for envoy_cli.maturity."""
import pytest

from envoy_cli.maturity import (
    MaturityError,
    VALID_LEVELS,
    get_maturity,
    list_maturity,
    remove_maturity,
    set_maturity,
)


@pytest.fixture()
def base(tmp_path):
    return tmp_path


def test_set_and_get_maturity(base):
    set_maturity(base, "production", "stable")
    assert get_maturity(base, "production") == "stable"


def test_set_creates_file(base):
    set_maturity(base, "staging", "beta")
    assert (base / "maturity.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(MaturityError, match="No maturity level"):
        get_maturity(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(MaturityError, match="must not be empty"):
        set_maturity(base, "", "stable")


def test_set_invalid_level_raises(base):
    with pytest.raises(MaturityError, match="Invalid level"):
        set_maturity(base, "dev", "unknown")


def test_all_valid_levels_accepted(base):
    for i, level in enumerate(VALID_LEVELS):
        set_maturity(base, f"env_{i}", level)
        assert get_maturity(base, f"env_{i}") == level


def test_overwrite_maturity(base):
    set_maturity(base, "production", "beta")
    set_maturity(base, "production", "stable")
    assert get_maturity(base, "production") == "stable"


def test_remove_maturity(base):
    set_maturity(base, "production", "stable")
    remove_maturity(base, "production")
    with pytest.raises(MaturityError):
        get_maturity(base, "production")


def test_remove_missing_raises(base):
    with pytest.raises(MaturityError, match="No maturity level"):
        remove_maturity(base, "ghost")


def test_remove_empty_name_raises(base):
    with pytest.raises(MaturityError, match="must not be empty"):
        remove_maturity(base, "")


def test_list_maturity_empty(base):
    assert list_maturity(base) == {}


def test_list_maturity_returns_all(base):
    set_maturity(base, "prod", "stable")
    set_maturity(base, "staging", "beta")
    result = list_maturity(base)
    assert result == {"prod": "stable", "staging": "beta"}


def test_get_empty_name_raises(base):
    with pytest.raises(MaturityError, match="must not be empty"):
        get_maturity(base, "")
