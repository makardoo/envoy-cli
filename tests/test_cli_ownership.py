"""Tests for envoy_cli.cli_ownership."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envoy_cli.cli_ownership import ownership_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_owner(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        result = runner.invoke(ownership_group, ["set", "production", "alice"])
    assert result.exit_code == 0
    assert "alice" in result.output


def test_set_owner_with_team(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        result = runner.invoke(ownership_group, ["set", "production", "alice", "--team", "ops"])
    assert result.exit_code == 0
    assert "ops" in result.output


def test_get_owner(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        runner.invoke(ownership_group, ["set", "staging", "bob", "--team", "dev"])
        result = runner.invoke(ownership_group, ["get", "staging"])
    assert result.exit_code == 0
    assert "bob" in result.output
    assert "dev" in result.output


def test_get_missing_exits_nonzero(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        result = runner.invoke(ownership_group, ["get", "ghost"])
    assert result.exit_code != 0


def test_remove_owner(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        runner.invoke(ownership_group, ["set", "dev", "carol"])
        result = runner.invoke(ownership_group, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        result = runner.invoke(ownership_group, ["remove", "nobody"])
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        result = runner.invoke(ownership_group, ["list"])
    assert result.exit_code == 0
    assert "No ownership" in result.output


def test_list_shows_entries(runner, tmp_path):
    with patch("envoy_cli.cli_ownership._BASE_DIR", tmp_path):
        runner.invoke(ownership_group, ["set", "prod", "alice"])
        runner.invoke(ownership_group, ["set", "staging", "bob"])
        result = runner.invoke(ownership_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output
