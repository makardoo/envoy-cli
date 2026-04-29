"""Tests for envoy_cli.cli_spotlight."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_spotlight import spotlight_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_add_spotlight(runner, tmp_path):
    result = runner.invoke(
        spotlight_group, ["add", "prod", "--reason", "go-live", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "Spotlighted 'prod'" in result.output


def test_add_spotlight_no_reason(runner, tmp_path):
    result = runner.invoke(spotlight_group, ["add", "dev", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0


def test_get_spotlight(runner, tmp_path):
    runner.invoke(spotlight_group, ["add", "prod", "--reason", "release", "--base-dir", str(tmp_path)])
    result = runner.invoke(spotlight_group, ["get", "prod", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "release" in result.output


def test_get_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(spotlight_group, ["get", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_remove_spotlight(runner, tmp_path):
    runner.invoke(spotlight_group, ["add", "prod", "--base-dir", str(tmp_path)])
    result = runner.invoke(spotlight_group, ["remove", "prod", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(spotlight_group, ["remove", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(spotlight_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No spotlighted" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(spotlight_group, ["add", "prod", "--reason", "go-live", "--base-dir", str(tmp_path)])
    runner.invoke(spotlight_group, ["add", "staging", "--base-dir", str(tmp_path)])
    result = runner.invoke(spotlight_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output
