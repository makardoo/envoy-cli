"""Tests for envoy_cli.cli_sensitivity."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_sensitivity import sensitivity_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_sensitivity(runner, tmp_path):
    result = runner.invoke(
        sensitivity_group,
        ["set", "prod", "secret", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "secret" in result.output


def test_set_invalid_level_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        sensitivity_group,
        ["set", "prod", "ultra", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code != 0


def test_get_sensitivity(runner, tmp_path):
    runner.invoke(
        sensitivity_group,
        ["set", "staging", "confidential", "--base-dir", str(tmp_path)],
    )
    result = runner.invoke(
        sensitivity_group,
        ["get", "staging", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "confidential" in result.output


def test_get_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        sensitivity_group,
        ["get", "ghost", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code != 0


def test_remove_sensitivity(runner, tmp_path):
    runner.invoke(
        sensitivity_group,
        ["set", "dev", "public", "--base-dir", str(tmp_path)],
    )
    result = runner.invoke(
        sensitivity_group,
        ["remove", "dev", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        sensitivity_group,
        ["remove", "ghost", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(
        sensitivity_group,
        ["list", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "No sensitivity" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(sensitivity_group, ["set", "prod", "secret", "--base-dir", str(tmp_path)])
    runner.invoke(sensitivity_group, ["set", "dev", "public", "--base-dir", str(tmp_path)])
    result = runner.invoke(
        sensitivity_group,
        ["list", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "secret" in result.output
    assert "dev" in result.output
    assert "public" in result.output
