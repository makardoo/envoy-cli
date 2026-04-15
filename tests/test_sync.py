"""Tests for the sync push/pull feature."""

import pytest
from pathlib import Path

from envoy_cli.sync import push_env, pull_env, list_remote_envs, get_remote_index
from envoy_cli.storage import save_env, load_env

PASSPHRASE = "sync-secret-passphrase"
SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"


@pytest.fixture
def tmp_dirs(tmp_path):
    local_dir = tmp_path / "local"
    remote_dir = tmp_path / "remote"
    local_dir.mkdir()
    remote_dir.mkdir()
    return str(local_dir), str(remote_dir)


def test_push_env_creates_remote_file(tmp_dirs):
    local_dir, remote_dir = tmp_dirs
    save_env("production", SAMPLE_ENV, store_dir=local_dir)
    remote_path = push_env("production", PASSPHRASE, remote_dir, store_dir=local_dir)
    assert Path(remote_path).exists()


def test_push_env_content_is_encrypted(tmp_dirs):
    local_dir, remote_dir = tmp_dirs
    save_env("production", SAMPLE_ENV, store_dir=local_dir)
    push_env("production", PASSPHRASE, remote_dir, store_dir=local_dir)

    remote_file = Path(remote_dir) / "production.env"
    content = remote_file.read_text()
    assert "localhost" not in content
    assert "abc123" not in content


def test_push_env_updates_remote_index(tmp_dirs):
    local_dir, remote_dir = tmp_dirs
    save_env("staging", SAMPLE_ENV, store_dir=local_dir)
    push_env("staging", PASSPHRASE, remote_dir, store_dir=local_dir)

    index = get_remote_index(remote_dir)
    assert "staging" in index
    assert index["staging"]["encrypted"] is True


def test_pull_env_restores_original_content(tmp_dirs):
    local_dir, remote_dir = tmp_dirs
    save_env("production", SAMPLE_ENV, store_dir=local_dir)
    push_env("production", PASSPHRASE, remote_dir, store_dir=local_dir)

    pull_local_dir = str(Path(local_dir).parent / "pulled")
    pull_env("production", PASSPHRASE, remote_dir, store_dir=pull_local_dir)
    restored = load_env("production", store_dir=pull_local_dir)

    assert "DB_HOST=localhost" in restored
    assert "SECRET_KEY=abc123" in restored


def test_pull_env_raises_if_remote_missing(tmp_dirs):
    local_dir, remote_dir = tmp_dirs
    with pytest.raises(FileNotFoundError, match="Remote env 'nonexistent' not found"):
        pull_env("nonexistent", PASSPHRASE, remote_dir, store_dir=local_dir)


def test_list_remote_envs_returns_names(tmp_dirs):
    local_dir, remote_dir = tmp_dirs
    save_env("dev", SAMPLE_ENV, store_dir=local_dir)
    save_env("prod", SAMPLE_ENV, store_dir=local_dir)
    push_env("dev", PASSPHRASE, remote_dir, store_dir=local_dir)
    push_env("prod", PASSPHRASE, remote_dir, store_dir=local_dir)

    names = list_remote_envs(remote_dir)
    assert "dev" in names
    assert "prod" in names


def test_list_remote_envs_empty_dir(tmp_dirs):
    _, remote_dir = tmp_dirs
    assert list_remote_envs(remote_dir) == []
