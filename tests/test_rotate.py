"""Tests for envoy_cli.rotate."""

import pytest
from click.testing import CliRunner

from envoy_cli.rotate import rotate_single, rotate_all
from envoy_cli.storage import save_env, load_env, list_envs
from envoy_cli.env_file import encrypt_env, decrypt_env


RAW_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=hunter2\n"
OLD_PASS = "old-passphrase"
NEW_PASS = "new-passphrase"


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path / "store")


def _seed(store, name, passphrase, content=RAW_ENV):
    encrypted = encrypt_env(content, passphrase)
    save_env(name, encrypted, store_dir=store)


# ---------------------------------------------------------------------------
# rotate_single
# ---------------------------------------------------------------------------

def test_rotate_single_can_decrypt_with_new_passphrase(store):
    _seed(store, "staging", OLD_PASS)
    rotate_single("staging", OLD_PASS, NEW_PASS, store_dir=store)
    re_encrypted = load_env("staging", store_dir=store)
    result = decrypt_env(re_encrypted, NEW_PASS)
    assert result == RAW_ENV


def test_rotate_single_old_passphrase_no_longer_works(store):
    _seed(store, "staging", OLD_PASS)
    rotate_single("staging", OLD_PASS, NEW_PASS, store_dir=store)
    re_encrypted = load_env("staging", store_dir=store)
    with pytest.raises(Exception):
        decrypt_env(re_encrypted, OLD_PASS)


def test_rotate_single_raises_if_env_not_found(store):
    with pytest.raises(FileNotFoundError):
        rotate_single("nonexistent", OLD_PASS, NEW_PASS, store_dir=store)


def test_rotate_single_raises_on_wrong_old_passphrase(store):
    _seed(store, "prod", OLD_PASS)
    with pytest.raises(Exception):
        rotate_single("prod", "wrong-pass", NEW_PASS, store_dir=store)


# ---------------------------------------------------------------------------
# rotate_all
# ---------------------------------------------------------------------------

def test_rotate_all_succeeds_for_all_envs(store):
    for name in ("dev", "staging", "prod"):
        _seed(store, name, OLD_PASS)

    succeeded, failed = rotate_all(OLD_PASS, NEW_PASS, store_dir=store)

    assert set(succeeded) == {"dev", "staging", "prod"}
    assert failed == []


def test_rotate_all_decrypts_correctly_after_rotation(store):
    _seed(store, "dev", OLD_PASS)
    rotate_all(OLD_PASS, NEW_PASS, store_dir=store)
    encrypted = load_env("dev", store_dir=store)
    assert decrypt_env(encrypted, NEW_PASS) == RAW_ENV


def test_rotate_all_partial_failure_reported(store):
    _seed(store, "good", OLD_PASS)
    # Seed 'bad' with a different passphrase so old_pass won't decrypt it
    _seed(store, "bad", "different-pass")

    succeeded, failed = rotate_all(OLD_PASS, NEW_PASS, store_dir=store)

    assert "good" in succeeded
    assert any(name == "bad" for name, _ in failed)


def test_rotate_all_empty_store_returns_empty_lists(store):
    succeeded, failed = rotate_all(OLD_PASS, NEW_PASS, store_dir=store)
    assert succeeded == []
    assert failed == []
