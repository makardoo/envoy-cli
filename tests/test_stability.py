"""Tests for envoy_cli.stability."""
import pytest

from envoy_cli.stability import (
    StabilityError,
    get_stability,
    list_stability,
    remove_stability,
    set_stability,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_stability(base):
    set_stability(base, "prod", "stable")
    assert get_stability(base, "prod") == "stable"


def test_set_creates_file(base, tmp_path):
    set_stability(base, "dev", "experimental")
    assert (tmp_path / "stability.json").exists()


def test_get_missing_returns_default(base):
    assert get_stability(base, "nonexistent") == "unstable"


def test_set_empty_name_raises(base):
    with pytest.raises(StabilityError, match="empty"):
        set_stability(base, "", "stable")


def test_get_empty_name_raises(base):
    with pytest.raises(StabilityError, match="empty"):
        get_stability(base, "")


def test_set_invalid_level_raises(base):
    with pytest.raises(StabilityError, match="invalid stability level"):
        set_stability(base, "prod", "legendary")


def test_remove_stability(base):
    set_stability(base, "staging", "frozen")
    remove_stability(base, "staging")
    assert get_stability(base, "staging") == "unstable"


def test_remove_missing_raises(base):
    with pytest.raises(StabilityError, match="no stability record"):
        remove_stability(base, "ghost")


def test_list_stability_empty(base):
    assert list_stability(base) == {}


def test_list_stability_returns_all(base):
    set_stability(base, "dev", "unstable")
    set_stability(base, "prod", "frozen")
    result = list_stability(base)
    assert result == {"dev": "unstable", "prod": "frozen"}


def test_overwrite_existing(base):
    set_stability(base, "dev", "unstable")
    set_stability(base, "dev", "stable")
    assert get_stability(base, "dev") == "stable"
