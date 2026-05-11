"""Tests for envoy_cli.cli_affinity."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_affinity import affinity_group


@pytest.fixture()
def runner():
    return CliRunner()


def _invoke(runner, tmp_path, *args):
    return runner.invoke(affinity_group, ["--base-dir", str(tmp_path), *args])


def test_set_affinity(runner, tmp_path):
    result = _invoke(runner, tmp_path, "set", "prod", "staging", "--strength", "strong")
    assert result.exit_code == 0
    assert "strong" in result.output


def test_set_affinity_default_strength(runner, tmp_path):
    result = _invoke(runner, tmp_path, "set", "prod", "dev")
    assert result.exit_code == 0
    assert "weak" in result.output


def test_set_invalid_strength_exits_nonzero(runner, tmp_path):
    result = _invoke(runner, tmp_path, "set", "prod", "dev", "--strength", "mega")
    assert result.exit_code != 0


def test_get_affinity(runner, tmp_path):
    _invoke(runner, tmp_path, "set", "prod", "staging", "--strength", "moderate")
    result = _invoke(runner, tmp_path, "get", "prod", "staging")
    assert result.exit_code == 0
    assert "moderate" in result.output


def test_get_missing_exits_nonzero(runner, tmp_path):
    result = _invoke(runner, tmp_path, "get", "prod", "staging")
    assert result.exit_code != 0


def test_remove_affinity(runner, tmp_path):
    _invoke(runner, tmp_path, "set", "prod", "staging")
    result = _invoke(runner, tmp_path, "remove", "prod", "staging")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    result = _invoke(runner, tmp_path, "remove", "prod", "staging")
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = _invoke(runner, tmp_path, "list", "prod")
    assert result.exit_code == 0
    assert "No affinities" in result.output


def test_list_shows_entries(runner, tmp_path):
    _invoke(runner, tmp_path, "set", "prod", "staging", "--strength", "strong")
    _invoke(runner, tmp_path, "set", "prod", "dev", "--strength", "weak")
    result = _invoke(runner, tmp_path, "list", "prod")
    assert result.exit_code == 0
    assert "staging" in result.output
    assert "dev" in result.output
