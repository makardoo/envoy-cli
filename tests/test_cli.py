"""Tests for the envoy CLI commands."""

import os
import pytest
from click.testing import CliRunner

from envoy_cli.cli import cli
from envoy_cli.storage import save_env, ensure_env_dir, get_env_dir


PASSPHRASE = "test-secret"
SAMPLE_ENV = "KEY1=value1\nKEY2=value2\n"


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Redirect the env store to a temp directory for every test."""
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path / ".envoy"))
    yield tmp_path


@pytest.fixture()
def sample_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(SAMPLE_ENV)
    return str(p)


def test_set_stores_env(sample_env_file):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["set", "production", sample_env_file, "--passphrase", PASSPHRASE]
    )
    assert result.exit_code == 0
    assert "production" in result.output


def test_get_decrypts_env(sample_env_file):
    runner = CliRunner()
    runner.invoke(cli, ["set", "staging", sample_env_file, "--passphrase", PASSPHRASE])
    result = runner.invoke(cli, ["get", "staging", "--passphrase", PASSPHRASE])
    assert result.exit_code == 0
    assert "KEY1" in result.output
    assert "value1" in result.output


def test_get_wrong_passphrase_exits_nonzero(sample_env_file):
    runner = CliRunner()
    runner.invoke(cli, ["set", "staging", sample_env_file, "--passphrase", PASSPHRASE])
    result = runner.invoke(cli, ["get", "staging", "--passphrase", "wrong-pass"])
    assert result.exit_code != 0


def test_get_writes_to_output_file(sample_env_file, tmp_path):
    runner = CliRunner()
    out_file = str(tmp_path / "out.env")
    runner.invoke(cli, ["set", "dev", sample_env_file, "--passphrase", PASSPHRASE])
    result = runner.invoke(
        cli, ["get", "dev", "--passphrase", PASSPHRASE, "--output", out_file]
    )
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    content = open(out_file).read()
    assert "KEY1" in content


def test_list_shows_stored_envs(sample_env_file):
    runner = CliRunner()
    runner.invoke(cli, ["set", "alpha", sample_env_file, "--passphrase", PASSPHRASE])
    runner.invoke(cli, ["set", "beta", sample_env_file, "--passphrase", PASSPHRASE])
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_empty(isolated_store):
    runner = CliRunner()
    result = runner.invoke(cli, ["list"])
    assert result.exit_code == 0
    assert "No environments" in result.output


def test_delete_removes_env(sample_env_file):
    runner = CliRunner()
    runner.invoke(cli, ["set", "to-delete", sample_env_file, "--passphrase", PASSPHRASE])
    result = runner.invoke(cli, ["delete", "to-delete"], input="y\n")
    assert result.exit_code == 0
    # Should no longer appear in list
    list_result = runner.invoke(cli, ["list"])
    assert "to-delete" not in list_result.output


def test_delete_nonexistent_exits_nonzero():
    runner = CliRunner()
    result = runner.invoke(cli, ["delete", "ghost"], input="y\n")
    assert result.exit_code != 0
