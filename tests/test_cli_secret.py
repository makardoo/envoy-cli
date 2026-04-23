"""Tests for envoy_cli.cli_secret."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envoy_cli.cli_secret import secret_group
from envoy_cli.storage import save_env
from envoy_cli.env_file import encrypt_env
import envoy_cli.storage as storage_mod


PASSPHRASE = "s3cr3t"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_mod, "_BASE_DIR", tmp_path)
    return tmp_path


def _seed(store: Path, env_name: str, content: str):
    encrypted = encrypt_env(content, PASSPHRASE)
    save_env(env_name, encrypted)


def test_scan_clean_env(runner, store):
    _seed(store, "dev", "PORT=8080\nDEBUG=true\n")
    result = runner.invoke(secret_group, ["scan", "dev", "-p", PASSPHRASE])
    assert result.exit_code == 0
    assert "No secrets detected" in result.output


def test_scan_dirty_env_exits_nonzero(runner, store):
    _seed(store, "prod", "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n")
    result = runner.invoke(secret_group, ["scan", "prod", "-p", PASSPHRASE])
    assert result.exit_code != 0
    assert "finding" in result.output.lower() or "aws-access-key" in result.output


def test_scan_show_values(runner, store):
    _seed(store, "prod", "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n")
    result = runner.invoke(
        secret_group, ["scan", "prod", "-p", PASSPHRASE, "--show-values"]
    )
    assert "AK" in result.output  # masked value starts with first 2 chars


def test_scan_missing_env_exits_nonzero(runner, store):
    result = runner.invoke(secret_group, ["scan", "ghost", "-p", PASSPHRASE])
    assert result.exit_code != 0
    assert "Error" in result.output or "error" in result.output


def test_scan_all_empty(runner, store):
    result = runner.invoke(secret_group, ["scan-all", "-p", PASSPHRASE])
    assert result.exit_code == 0
    assert "No env files found" in result.output


def test_scan_all_with_clean_env(runner, store):
    _seed(store, "staging", "PORT=9000\n")
    result = runner.invoke(secret_group, ["scan-all", "-p", PASSPHRASE])
    assert result.exit_code == 0
    assert "clean" in result.output


def test_scan_all_exits_nonzero_when_dirty(runner, store):
    _seed(store, "prod", "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n")
    result = runner.invoke(secret_group, ["scan-all", "-p", PASSPHRASE])
    assert result.exit_code != 0
