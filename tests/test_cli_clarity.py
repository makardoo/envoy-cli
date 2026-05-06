"""Tests for envoy_cli.cli_clarity."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_clarity import clarity_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_clarity(runner, tmp_path):
    result = runner.invoke(
        clarity_group, ["set", "prod", "documented", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "documented" in result.output


def test_set_invalid_level_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        clarity_group, ["set", "prod", "brilliant", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_get_clarity(runner, tmp_path):
    runner.invoke(clarity_group, ["set", "staging", "minimal", "--note", "wip", "--base-dir", str(tmp_path)])
    result = runner.invoke(clarity_group, ["get", "staging", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "minimal" in result.output
    assert "wip" in result.output


def test_get_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(clarity_group, ["get", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_remove_clarity(runner, tmp_path):
    runner.invoke(clarity_group, ["set", "dev", "opaque", "--base-dir", str(tmp_path)])
    result = runner.invoke(clarity_group, ["remove", "dev", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_empty(runner, tmp_path):
    result = runner.invoke(clarity_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No clarity records" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(clarity_group, ["set", "prod", "exemplary", "--base-dir", str(tmp_path)])
    runner.invoke(clarity_group, ["set", "dev", "opaque", "--base-dir", str(tmp_path)])
    result = runner.invoke(clarity_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "dev" in result.output
