import pytest
from pathlib import Path
from envoy_cli.tier import (
    set_tier, get_tier, remove_tier, list_tiers, TierError
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_tier(base):
    set_tier(base, "prod", "enterprise")
    assert get_tier(base, "prod") == "enterprise"


def test_set_creates_file(base):
    set_tier(base, "staging", "pro")
    assert (Path(base) / "tiers.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(TierError, match="No tier set"):
        get_tier(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(TierError, match="must not be empty"):
        set_tier(base, "", "pro")


def test_set_invalid_tier_raises(base):
    with pytest.raises(TierError, match="Invalid tier"):
        set_tier(base, "dev", "superduper")


def test_remove_tier(base):
    set_tier(base, "dev", "free")
    remove_tier(base, "dev")
    with pytest.raises(TierError):
        get_tier(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(TierError, match="No tier set"):
        remove_tier(base, "ghost")


def test_list_tiers_empty(base):
    assert list_tiers(base) == {}


def test_list_tiers_returns_all(base):
    set_tier(base, "prod", "enterprise")
    set_tier(base, "staging", "pro")
    result = list_tiers(base)
    assert result == {"prod": "enterprise", "staging": "pro"}


def test_overwrite_tier(base):
    set_tier(base, "prod", "free")
    set_tier(base, "prod", "enterprise")
    assert get_tier(base, "prod") == "enterprise"
