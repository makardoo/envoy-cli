import pytest
from pathlib import Path
from envoy_cli.access import (
    set_permission, get_permission, list_permissions,
    remove_permission, check_permission, AccessError, _access_path
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_permission(base):
    set_permission(base, "prod", "alice", True, True)
    p = get_permission(base, "prod", "alice")
    assert p["read"] is True
    assert p["write"] is True


def test_set_creates_file(base):
    set_permission(base, "prod", "alice", True, False)
    assert _access_path(base).exists()


def test_get_missing_raises(base):
    with pytest.raises(AccessError):
        get_permission(base, "prod", "alice")


def test_set_read_only(base):
    set_permission(base, "staging", "bob", True, False)
    p = get_permission(base, "staging", "bob")
    assert p["read"] is True
    assert p["write"] is False


def test_overwrite_permission(base):
    set_permission(base, "prod", "alice", True, True)
    set_permission(base, "prod", "alice", True, False)
    p = get_permission(base, "prod", "alice")
    assert p["write"] is False


def test_list_permissions(base):
    set_permission(base, "prod", "alice", True, True)
    set_permission(base, "prod", "bob", True, False)
    perms = list_permissions(base, "prod")
    assert "alice" in perms
    assert "bob" in perms


def test_list_permissions_empty(base):
    assert list_permissions(base, "nonexistent") == {}


def test_remove_permission(base):
    set_permission(base, "prod", "alice", True, True)
    remove_permission(base, "prod", "alice")
    with pytest.raises(AccessError):
        get_permission(base, "prod", "alice")


def test_remove_missing_raises(base):
    with pytest.raises(AccessError):
        remove_permission(base, "prod", "ghost")


def test_check_permission_allowed(base):
    set_permission(base, "prod", "alice", True, True)
    assert check_permission(base, "prod", "alice", "write") is True


def test_check_permission_denied(base):
    set_permission(base, "prod", "alice", True, False)
    assert check_permission(base, "prod", "alice", "write") is False


def test_check_permission_missing_entry_defaults_true(base):
    assert check_permission(base, "prod", "unknown", "read") is True


def test_empty_env_name_raises(base):
    with pytest.raises(AccessError):
        set_permission(base, "", "alice", True, True)


def test_empty_profile_raises(base):
    with pytest.raises(AccessError):
        set_permission(base, "prod", "", True, True)
