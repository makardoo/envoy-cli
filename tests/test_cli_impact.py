"""Tests for envoy_cli.cli_impact."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_impact import impact_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_impact(runner, tmp_path):
    result = runner.invoke(
        impact_group, ["set", "prod", "critical", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "critical" in result.output


def test_set_invalid_level_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        impact_group, ["set", "prod", "extreme", "--base-dir", str(tmp_path)]
    )
    # Click Choice validation rejects unknown values before our code
    assert result.exit_code != 0


def test_get_impact(runner, tmp_path):
    runner.invoke(
        impact_group, ["set", "staging", "high", "--base-dir", str(tmp_path)]
    )
    result = runner.invoke(
        impact_group, ["get", "staging", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "high" in result.output


def test_get_missing_returns_default(runner, tmp_path):
    result = runner.invoke(
        impact_group, ["get", "ghost", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "low" in result.output


def test_remove_impact(runner, tmp_path):
    runner.invoke(
        impact_group, ["set", "dev", "medium", "--base-dir", str(tmp_path)]
    )
    result = runner.invoke(
        impact_group, ["remove", "dev", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        impact_group, ["remove", "nope", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 1


def test_list_empty(runner, tmp_path):
    result = runner.invoke(
        impact_group, ["list", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "No impact" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(impact_group, ["set", "prod", "critical", "--base-dir", str(tmp_path)])
    runner.invoke(impact_group, ["set", "dev", "low", "--base-dir", str(tmp_path)])
    result = runner.invoke(impact_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "critical" in result.output
    assert "dev" in result.output
