import pytest
from envoy_cli.region import (
    set_region, get_region, remove_region, list_regions, RegionError
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_region(base):
    set_region(base, "production", "us-east")
    assert get_region(base, "production") == "us-east"


def test_set_creates_file(base):
    from pathlib import Path
    set_region(base, "staging", "eu-west")
    assert (Path(base) / "regions.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(RegionError, match="No region"):
        get_region(base, "missing")


def test_set_invalid_region_raises(base):
    with pytest.raises(RegionError, match="Invalid region"):
        set_region(base, "dev", "mars-north")


def test_set_empty_name_raises(base):
    with pytest.raises(RegionError, match="must not be empty"):
        set_region(base, "", "us-east")


def test_remove_region(base):
    set_region(base, "dev", "local")
    remove_region(base, "dev")
    with pytest.raises(RegionError):
        get_region(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(RegionError, match="No region"):
        remove_region(base, "ghost")


def test_list_regions_empty(base):
    assert list_regions(base) == {}


def test_list_regions_multiple(base):
    set_region(base, "prod", "us-east")
    set_region(base, "staging", "eu-west")
    data = list_regions(base)
    assert data["prod"] == "us-east"
    assert data["staging"] == "eu-west"


def test_overwrite_region(base):
    set_region(base, "prod", "us-east")
    set_region(base, "prod", "ap-south")
    assert get_region(base, "prod") == "ap-south"
