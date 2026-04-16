"""Tests for envoy_cli.lock module."""

import pytest

from envoy_cli.lock import (
    LockError,
    get_lock_info,
    is_locked,
    list_locked_envs,
    lock_env,
    unlock_env,
)


@pytest.fixture
def lock_dir(tmp_path):
    return str(tmp_path)


def test_lock_env_marks_as_locked(lock_dir):
    lock_env("production", reason="deploy freeze", env_dir=lock_dir)
    assert is_locked("production", env_dir=lock_dir)


def test_unlock_env_removes_lock(lock_dir):
    lock_env("staging", env_dir=lock_dir)
    unlock_env("staging", env_dir=lock_dir)
    assert not is_locked("staging", env_dir=lock_dir)


def test_lock_already_locked_raises(lock_dir):
    lock_env("production", env_dir=lock_dir)
    with pytest.raises(LockError, match="already locked"):
        lock_env("production", env_dir=lock_dir)


def test_unlock_not_locked_raises(lock_dir):
    with pytest.raises(LockError, match="not locked"):
        unlock_env("nonexistent", env_dir=lock_dir)


def test_lock_empty_name_raises(lock_dir):
    with pytest.raises(LockError, match="must not be empty"):
        lock_env("", env_dir=lock_dir)


def test_get_lock_info_returns_metadata(lock_dir):
    lock_env("production", reason="hotfix", env_dir=lock_dir)
    info = get_lock_info("production", env_dir=lock_dir)
    assert info is not None
    assert info["reason"] == "hotfix"
    assert "locked_at" in info


def test_get_lock_info_returns_none_if_not_locked(lock_dir):
    assert get_lock_info("staging", env_dir=lock_dir) is None


def test_is_locked_returns_false_for_unknown(lock_dir):
    assert not is_locked("unknown", env_dir=lock_dir)


def test_list_locked_envs_returns_all(lock_dir):
    lock_env("prod", reason="freeze", env_dir=lock_dir)
    lock_env("staging", reason="testing", env_dir=lock_dir)
    locked = list_locked_envs(env_dir=lock_dir)
    assert set(locked.keys()) == {"prod", "staging"}


def test_list_locked_envs_empty_if_none(lock_dir):
    assert list_locked_envs(env_dir=lock_dir) == {}


def test_lock_persists_across_calls(lock_dir):
    lock_env("prod", reason="persistent", env_dir=lock_dir)
    # Simulate a fresh call by re-reading
    assert is_locked("prod", env_dir=lock_dir)
    info = get_lock_info("prod", env_dir=lock_dir)
    assert info["reason"] == "persistent"
