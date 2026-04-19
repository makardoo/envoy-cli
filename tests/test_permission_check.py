"""Tests for envoy_cli.permission_check."""
from pathlib import Path

import pytest

from envoy_cli.access import set_permission
from envoy_cli.permission_check import (
    PermissionDenied,
    assert_read,
    assert_readwrite,
    check_permission,
    has_permission,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_check_permission_readwrite_granted(base: Path) -> None:
    set_permission(base, "prod", "alice", "readwrite")
    check_permission(base, "prod", "alice", "readwrite")  # should not raise


def test_check_permission_read_granted(base: Path) -> None:
    set_permission(base, "prod", "bob", "read")
    check_permission(base, "prod", "bob", "read")  # should not raise


def test_check_permission_read_satisfies_read(base: Path) -> None:
    set_permission(base, "staging", "carol", "read")
    check_permission(base, "staging", "carol", "read")  # read >= read


def test_check_permission_read_insufficient_for_readwrite(base: Path) -> None:
    set_permission(base, "prod", "dave", "read")
    with pytest.raises(PermissionDenied, match="read-only"):
        check_permission(base, "prod", "dave", "readwrite")


def test_check_permission_no_entry_raises(base: Path) -> None:
    with pytest.raises(PermissionDenied, match="no access"):
        check_permission(base, "prod", "unknown", "read")


def test_check_permission_invalid_level_raises(base: Path) -> None:
    with pytest.raises(ValueError, match="Unknown permission level"):
        check_permission(base, "prod", "alice", "admin")


def test_has_permission_true(base: Path) -> None:
    set_permission(base, "dev", "eve", "readwrite")
    assert has_permission(base, "dev", "eve", "readwrite") is True


def test_has_permission_false_no_entry(base: Path) -> None:
    assert has_permission(base, "dev", "nobody", "read") is False


def test_has_permission_false_insufficient(base: Path) -> None:
    set_permission(base, "dev", "frank", "read")
    assert has_permission(base, "dev", "frank", "readwrite") is False


def test_assert_readwrite_passes(base: Path) -> None:
    set_permission(base, "prod", "grace", "readwrite")
    assert_readwrite(base, "prod", "grace")


def test_assert_read_passes(base: Path) -> None:
    set_permission(base, "prod", "heidi", "read")
    assert_read(base, "prod", "heidi")


def test_assert_readwrite_raises_for_read_only(base: Path) -> None:
    set_permission(base, "prod", "ivan", "read")
    with pytest.raises(PermissionDenied):
        assert_readwrite(base, "prod", "ivan")
