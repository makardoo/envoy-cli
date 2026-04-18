"""Tests for envoy_cli.cli_history."""
import pytest
from click.testing import CliRunner
from envoy_cli.cli_history import history_group
from envoy_cli.history import record_change


@pytest.fixture
def runner():
    return CliRunner()


def test_show_empty(runner, tmp_path):
    result = runner.invoke(
        history_group, ["show", "prod", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "No history" in result.output


def test_show_displays_entries(runner, tmp_path):
    record_change(str(tmp_path), "prod", "push", actor="ci")
    result = runner.invoke(
        history_group, ["show", "prod", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "push" in result.output
    assert "ci" in result.output


def test_show_limit(runner, tmp_path):
    for i in range(5):
        record_change(str(tmp_path), "prod", f"action_{i}")
    result = runner.invoke(
        history_group, ["show", "prod", "--limit", "2", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert result.output.count("action_") == 2


def test_clear_cmd(runner, tmp_path):
    record_change(str(tmp_path), "prod", "push")
    result = runner.invoke(
        history_group, ["clear", "prod", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "1" in result.output


def test_record_cmd(runner, tmp_path):
    result = runner.invoke(
        history_group,
        ["record", "prod", "deploy", "--actor", "bot", "--note", "v2", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "deploy" in result.output


def test_record_cmd_empty_name_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        history_group,
        ["record", "", "push", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code != 0
