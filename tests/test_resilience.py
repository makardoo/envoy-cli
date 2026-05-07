"""Tests for envoy_cli.resilience."""
import pytest
from pathlib import Path
from envoy_cli.resilience import (
    ResilienceError,
    VALID_LEVELS,
    set_resilience,
    get_resilience,
    remove_resilience,
    list_resilience,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_resilience(base):
    set_resilience(base, "prod", "robust")
    assert get_resilience(base, "prod") == "robust"


def test_set_creates_file(base):
    set_resilience(base, "staging", "moderate")
    assert (Path(base) / "resilience.json").exists()


def test_get_missing_returns_default(base):
    assert get_resilience(base, "nonexistent") == "fragile"


def test_set_empty_name_raises(base):
    with pytest.raises(ResilienceError, match="empty"):
        set_resilience(base, "", "robust")


def test_get_empty_name_raises(base):
    with pytest.raises(ResilienceError, match="empty"):
        get_resilience(base, "")


def test_set_invalid_level_raises(base):
    with pytest.raises(ResilienceError, match="invalid level"):
        set_resilience(base, "dev", "invincible")


def test_remove_resilience(base):
    set_resilience(base, "dev", "hardened")
    remove_resilience(base, "dev")
    assert get_resilience(base, "dev") == "fragile"


def test_remove_missing_raises(base):
    with pytest.raises(ResilienceError):
        remove_resilience(base, "ghost")


def test_list_resilience_empty(base):
    assert list_resilience(base) == {}


def test_list_resilience_multiple(base):
    set_resilience(base, "prod", "hardened")
    set_resilience(base, "staging", "moderate")
    records = list_resilience(base)
    assert records == {"prod": "hardened", "staging": "moderate"}


def test_overwrite_resilience(base):
    set_resilience(base, "prod", "fragile")
    set_resilience(base, "prod", "robust")
    assert get_resilience(base, "prod") == "robust"


def test_all_valid_levels_accepted(base):
    for i, level in enumerate(VALID_LEVELS):
        set_resilience(base, f"env_{i}", level)
        assert get_resilience(base, f"env_{i}") == level
