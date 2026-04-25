"""Tests for envoy_cli.cli_trust."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_trust import trust_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_trust(runner, tmp_path):
    result = runner.invoke(
        trust_group, ["set", "prod", "high", "--dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "high" in result.output


def test_set_invalid_level_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        trust_group, ["set", "prod", "super", "--dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_get_trust(runner, tmp_path):
    runner.invoke(trust_group, ["set", "dev", "low", "--dir", str(tmp_path)])
    result = runner.invoke(trust_group, ["get", "dev", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "low" in result.output


def test_get_missing_returns_untrusted(runner, tmp_path):
    result = runner.invoke(trust_group, ["get", "ghost", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "untrusted" in result.output


def test_remove_trust(runner, tmp_path):
    runner.invoke(trust_group, ["set", "staging", "medium", "--dir", str(tmp_path)])
    result = runner.invoke(
        trust_group, ["remove", "staging", "--dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        trust_group, ["remove", "ghost", "--dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(trust_group, ["list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No trust records" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(trust_group, ["set", "prod", "verified", "--dir", str(tmp_path)])
    runner.invoke(trust_group, ["set", "dev", "low", "--dir", str(tmp_path)])
    result = runner.invoke(trust_group, ["list", "--dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "verified" in result.output
    assert "dev" in result.output
    assert "low" in result.output
