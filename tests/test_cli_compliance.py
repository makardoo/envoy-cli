"""Tests for envoy_cli.cli_compliance CLI commands."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envoy_cli.cli_compliance import compliance_group
from envoy_cli.compliance import set_required_keys


@pytest.fixture()
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_DIR", str(tmp_path))
    # Patch get_env_dir to return tmp_path
    import envoy_cli.cli_compliance as mod
    monkeypatch.setattr(mod, "get_env_dir", lambda: str(tmp_path))
    return CliRunner(), tmp_path


def test_set_policy(runner):
    cli_runner, base = runner
    result = cli_runner.invoke(compliance_group, ["set", "prod", "DB_URL", "SECRET_KEY"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_get_policy(runner):
    cli_runner, base = runner
    set_required_keys(base, "prod", ["DB_URL", "API_KEY"])
    result = cli_runner.invoke(compliance_group, ["get", "prod"])
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "API_KEY" in result.output


def test_get_missing_policy_exits_nonzero(runner):
    cli_runner, base = runner
    result = cli_runner.invoke(compliance_group, ["get", "ghost"])
    assert result.exit_code != 0


def test_remove_policy(runner):
    cli_runner, base = runner
    set_required_keys(base, "prod", ["KEY"])
    result = cli_runner.invoke(compliance_group, ["remove", "prod"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner):
    cli_runner, base = runner
    result = cli_runner.invoke(compliance_group, ["remove", "ghost"])
    assert result.exit_code != 0


def test_list_empty(runner):
    cli_runner, base = runner
    result = cli_runner.invoke(compliance_group, ["list"])
    assert result.exit_code == 0
    assert "No compliance" in result.output


def test_list_shows_entries(runner):
    cli_runner, base = runner
    set_required_keys(base, "prod", ["A", "B"])
    set_required_keys(base, "staging", ["C"])
    result = cli_runner.invoke(compliance_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output


def test_check_passes(runner, tmp_path):
    cli_runner, base = runner
    set_required_keys(base, "prod", ["DB_URL"])
    env_file = tmp_path / "test.env"
    env_file.write_text("DB_URL=postgres://localhost/db\n")
    result = cli_runner.invoke(
        compliance_group, ["check", "prod", "--file", str(env_file)]
    )
    assert result.exit_code == 0
    assert "passes" in result.output


def test_check_fails_missing_key(runner, tmp_path):
    cli_runner, base = runner
    set_required_keys(base, "prod", ["SECRET_KEY"])
    env_file = tmp_path / "test.env"
    env_file.write_text("DB_URL=postgres://localhost/db\n")
    result = cli_runner.invoke(
        compliance_group, ["check", "prod", "--file", str(env_file)]
    )
    assert result.exit_code != 0
    assert "SECRET_KEY" in result.output
