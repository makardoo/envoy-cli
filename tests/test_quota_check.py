"""Tests for envoy_cli.quota_check."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.quota_check import check_quota, count_keys, QuotaExceeded
from envoy_cli.cli_quota_check import quota_check_group
from envoy_cli.storage import save_env
from envoy_cli.env_file import encrypt_env
from envoy_cli.quota import set_quota


PASSPHRASE = "s3cr3t"


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def _seed(store: str, name: str, content: str) -> None:
    encrypted = encrypt_env(content, PASSPHRASE)
    save_env(name, encrypted, base_dir=store)


# ---------------------------------------------------------------------------
# count_keys
# ---------------------------------------------------------------------------

def test_count_keys_basic():
    content = "FOO=bar\nBAZ=qux\n"
    assert count_keys(content) == 2


def test_count_keys_ignores_comments_and_blanks():
    content = "# comment\n\nFOO=bar\n"
    assert count_keys(content) == 1


def test_count_keys_empty():
    assert count_keys("") == 0


# ---------------------------------------------------------------------------
# check_quota — no quota set
# ---------------------------------------------------------------------------

def test_check_quota_no_quota(store):
    _seed(store, "dev", "A=1\nB=2\n")
    result = check_quota("dev", PASSPHRASE, base_dir=store)
    assert result.actual == 2
    assert result.quota is None
    assert result.exceeded is False


def test_check_quota_within_limit(store):
    _seed(store, "dev", "A=1\nB=2\n")
    set_quota("dev", 5, base_dir=store)
    result = check_quota("dev", PASSPHRASE, base_dir=store)
    assert result.exceeded is False
    assert result.actual == 2
    assert result.quota == 5


def test_check_quota_exceeded(store):
    _seed(store, "dev", "A=1\nB=2\nC=3\n")
    set_quota("dev", 2, base_dir=store)
    result = check_quota("dev", PASSPHRASE, base_dir=store)
    assert result.exceeded is True


def test_check_quota_raise_if_exceeded(store):
    _seed(store, "dev", "A=1\nB=2\nC=3\n")
    set_quota("dev", 1, base_dir=store)
    with pytest.raises(QuotaExceeded):
        check_quota("dev", PASSPHRASE, base_dir=store, raise_if_exceeded=True)


def test_check_quota_no_raise_when_not_exceeded(store):
    _seed(store, "dev", "A=1\n")
    set_quota("dev", 5, base_dir=store)
    # Should not raise
    result = check_quota("dev", PASSPHRASE, base_dir=store, raise_if_exceeded=True)
    assert not result.exceeded


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def test_cli_check_ok(store):
    _seed(store, "dev", "A=1\n")
    set_quota("dev", 5, base_dir=store)
    runner = CliRunner()
    result = runner.invoke(
        quota_check_group,
        ["check", "dev", "--passphrase", PASSPHRASE, "--base-dir", store],
    )
    assert result.exit_code == 0
    assert "OK" in result.output


def test_cli_check_exceeded_strict(store):
    _seed(store, "dev", "A=1\nB=2\nC=3\n")
    set_quota("dev", 1, base_dir=store)
    runner = CliRunner()
    result = runner.invoke(
        quota_check_group,
        ["check", "dev", "--passphrase", PASSPHRASE, "--base-dir", store, "--strict"],
    )
    assert result.exit_code != 0


def test_cli_check_all_empty(store):
    runner = CliRunner()
    result = runner.invoke(
        quota_check_group,
        ["check-all", "--passphrase", PASSPHRASE, "--base-dir", store],
    )
    assert result.exit_code == 0
    assert "No environments" in result.output
