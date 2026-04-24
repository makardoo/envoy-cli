"""Tests for envoy_cli.cli_lifecycle."""
import os
import pytest
from click.testing import CliRunner

from envoy_cli.cli_lifecycle import lifecycle_group


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_BASE_DIR", str(tmp_path))
    return CliRunner()


def test_set_state(runner):
    result = runner.invoke(lifecycle_group, ["set", "myenv", "draft"])
    assert result.exit_code == 0
    assert "draft" in result.output


def test_set_invalid_state_exits_nonzero(runner):
    result = runner.invoke(lifecycle_group, ["set", "myenv", "invalid"])
    assert result.exit_code != 0


def test_set_invalid_transition_exits_nonzero(runner):
    runner.invoke(lifecycle_group, ["set", "myenv", "draft"])
    result = runner.invoke(lifecycle_group, ["set", "myenv", "retired"])
    assert result.exit_code == 1
    assert "Cannot transition" in result.output


def test_get_state(runner):
    runner.invoke(lifecycle_group, ["set", "myenv", "draft"])
    result = runner.invoke(lifecycle_group, ["get", "myenv"])
    assert result.exit_code == 0
    assert "draft" in result.output


def test_get_missing_exits_nonzero(runner):
    result = runner.invoke(lifecycle_group, ["get", "ghost"])
    assert result.exit_code == 1


def test_remove_state(runner):
    runner.invoke(lifecycle_group, ["set", "myenv", "draft"])
    result = runner.invoke(lifecycle_group, ["remove", "myenv"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner):
    result = runner.invoke(lifecycle_group, ["remove", "ghost"])
    assert result.exit_code == 1


def test_list_empty(runner):
    result = runner.invoke(lifecycle_group, ["list"])
    assert result.exit_code == 0
    assert "No lifecycle" in result.output


def test_list_shows_entries(runner):
    runner.invoke(lifecycle_group, ["set", "alpha", "draft"])
    runner.invoke(lifecycle_group, ["set", "beta", "draft"])
    result = runner.invoke(lifecycle_group, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_transitions_cmd(runner):
    result = runner.invoke(lifecycle_group, ["transitions"])
    assert result.exit_code == 0
    assert "draft" in result.output
    assert "active" in result.output
