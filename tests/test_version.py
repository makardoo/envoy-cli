"""Tests for envoy_cli.version."""
import pytest
from pathlib import Path
from envoy_cli.version import (
    record_version,
    list_versions,
    get_version,
    delete_versions,
    VersionError,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_record_creates_file(base):
    record_version(base, "prod", "KEY=val")
    p = Path(base) / ".versions" / "prod.json"
    assert p.exists()


def test_record_returns_entry(base):
    entry = record_version(base, "prod", "KEY=val", message="init")
    assert entry["version"] == 1
    assert entry["content"] == "KEY=val"
    assert entry["message"] == "init"
    assert entry["timestamp"] > 0


def test_record_increments_version(base):
    record_version(base, "prod", "A=1")
    e2 = record_version(base, "prod", "A=2")
    assert e2["version"] == 2


def test_list_versions_empty(base):
    assert list_versions(base, "prod") == []


def test_list_versions_returns_all(base):
    record_version(base, "prod", "A=1")
    record_version(base, "prod", "A=2")
    versions = list_versions(base, "prod")
    assert len(versions) == 2


def test_get_version_returns_correct(base):
    record_version(base, "prod", "A=1")
    record_version(base, "prod", "A=2")
    v = get_version(base, "prod", 1)
    assert v["content"] == "A=1"


def test_get_version_missing_raises(base):
    record_version(base, "prod", "A=1")
    with pytest.raises(VersionError, match="Version 99 not found"):
        get_version(base, "prod", 99)


def test_delete_versions_removes_file(base):
    record_version(base, "prod", "A=1")
    delete_versions(base, "prod")
    assert list_versions(base, "prod") == []


def test_delete_versions_nonexistent_ok(base):
    delete_versions(base, "ghost")  # should not raise


def test_empty_name_raises(base):
    with pytest.raises(VersionError):
        record_version(base, "  ", "A=1")


def test_versions_isolated_per_env(base):
    record_version(base, "prod", "A=1")
    record_version(base, "staging", "B=2")
    assert len(list_versions(base, "prod")) == 1
    assert len(list_versions(base, "staging")) == 1
