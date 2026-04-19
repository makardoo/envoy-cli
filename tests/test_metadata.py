"""Tests for envoy_cli.metadata."""
import pytest
from envoy_cli.metadata import (
    MetadataError,
    set_metadata,
    get_metadata,
    get_all_metadata,
    remove_metadata,
    list_all_metadata,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_metadata(base):
    set_metadata(base, "prod", "owner", "alice")
    assert get_metadata(base, "prod", "owner") == "alice"


def test_set_creates_file(base):
    from pathlib import Path
    set_metadata(base, "staging", "team", "backend")
    assert (Path(base) / "metadata.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(MetadataError):
        get_metadata(base, "prod", "owner")


def test_set_empty_name_raises(base):
    with pytest.raises(MetadataError):
        set_metadata(base, "", "key", "val")


def test_set_empty_key_raises(base):
    with pytest.raises(MetadataError):
        set_metadata(base, "prod", "", "val")


def test_overwrite_metadata(base):
    set_metadata(base, "prod", "owner", "alice")
    set_metadata(base, "prod", "owner", "bob")
    assert get_metadata(base, "prod", "owner") == "bob"


def test_get_all_metadata(base):
    set_metadata(base, "prod", "owner", "alice")
    set_metadata(base, "prod", "team", "ops")
    meta = get_all_metadata(base, "prod")
    assert meta == {"owner": "alice", "team": "ops"}


def test_get_all_metadata_empty(base):
    assert get_all_metadata(base, "prod") == {}


def test_remove_metadata(base):
    set_metadata(base, "prod", "owner", "alice")
    remove_metadata(base, "prod", "owner")
    with pytest.raises(MetadataError):
        get_metadata(base, "prod", "owner")


def test_remove_cleans_up_empty_env(base):
    set_metadata(base, "prod", "owner", "alice")
    remove_metadata(base, "prod", "owner")
    assert "prod" not in list_all_metadata(base)


def test_remove_missing_raises(base):
    with pytest.raises(MetadataError):
        remove_metadata(base, "prod", "owner")


def test_list_all_metadata(base):
    set_metadata(base, "prod", "owner", "alice")
    set_metadata(base, "staging", "owner", "bob")
    all_meta = list_all_metadata(base)
    assert "prod" in all_meta
    assert "staging" in all_meta


def test_list_all_empty(base):
    assert list_all_metadata(base) == {}
