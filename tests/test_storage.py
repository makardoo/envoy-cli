"""Tests for the storage module."""

import pytest
from pathlib import Path

from envoy_cli.storage import (
    save_env,
    load_env,
    list_envs,
    delete_env,
    env_file_path,
    ensure_env_dir,
)


@pytest.fixture
def tmp_store(tmp_path):
    """Provide a temporary directory as the storage base."""
    return tmp_path / "envoy_store"


def test_save_env_creates_file(tmp_store):
    path = save_env("production", "encrypted_data_here", base_dir=tmp_store)
    assert path.exists()
    assert path.read_text() == "encrypted_data_here"


def test_save_env_creates_directory_if_missing(tmp_store):
    assert not tmp_store.exists()
    save_env("staging", "some_content", base_dir=tmp_store)
    assert tmp_store.exists()


def test_load_env_returns_content(tmp_store):
    save_env("staging", "secret_payload", base_dir=tmp_store)
    content = load_env("staging", base_dir=tmp_store)
    assert content == "secret_payload"


def test_load_env_raises_if_not_found(tmp_store):
    with pytest.raises(FileNotFoundError, match="No env file found for 'missing'"):
        load_env("missing", base_dir=tmp_store)


def test_list_envs_returns_names(tmp_store):
    save_env("production", "a", base_dir=tmp_store)
    save_env("staging", "b", base_dir=tmp_store)
    names = list_envs(base_dir=tmp_store)
    assert set(names) == {"production", "staging"}


def test_list_envs_empty_when_no_dir(tmp_store):
    result = list_envs(base_dir=tmp_store)
    assert result == []


def test_delete_env_removes_file(tmp_store):
    save_env("production", "data", base_dir=tmp_store)
    deleted = delete_env("production", base_dir=tmp_store)
    assert deleted is True
    assert not env_file_path("production", base_dir=tmp_store).exists()


def test_delete_env_returns_false_if_not_found(tmp_store):
    result = delete_env("nonexistent", base_dir=tmp_store)
    assert result is False


def test_env_file_path_sanitizes_slashes(tmp_store):
    path = env_file_path("org/project", base_dir=tmp_store)
    assert "/" not in path.name
    assert path.name == "org_project.enc"


def test_save_and_load_roundtrip(tmp_store):
    payload = "ENC:abc123:def456"
    save_env("local", payload, base_dir=tmp_store)
    assert load_env("local", base_dir=tmp_store) == payload
