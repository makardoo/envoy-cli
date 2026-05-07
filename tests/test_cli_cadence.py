"""Tests for envoy_cli.cli_cadence."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_cadence import cadence_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_cadence(runner, tmp_path):
    result = runner.invoke(
        cadence_group, ["set", "prod", "daily", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "daily" in result.output


def test_set_invalid_cadence_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        cadence_group, ["set", "prod", "quarterly", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_get_cadence(runner, tmp_path):
    runner.invoke(cadence_group, ["set", "dev", "weekly", "--base-dir", str(tmp_path)])
    result = runner.invoke(cadence_group, ["get", "dev", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "weekly" in result.output


def test_get_missing_returns_manual(runner, tmp_path):
    result = runner.invoke(
        cadence_group, ["get", "ghost", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "manual" in result.output


def test_remove_cadence(runner, tmp_path):
    runner.invoke(cadence_group, ["set", "staging", "hourly", "--base-dir", str(tmp_path)])
    result = runner.invoke(
        cadence_group, ["remove", "staging", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        cadence_group, ["remove", "ghost", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(cadence_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No cadences" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(cadence_group, ["set", "prod", "daily", "--base-dir", str(tmp_path)])
    runner.invoke(cadence_group, ["set", "dev", "manual", "--base-dir", str(tmp_path)])
    result = runner.invoke(cadence_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "daily" in result.output
    assert "dev" in result.output
