import os
import pytest
from click.testing import CliRunner
from envoy_cli.cli_schedule import schedule_group


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return CliRunner()


def test_add_schedule(runner):
    result = runner.invoke(schedule_group, ["add", "staging", "--cron", "0 * * * *"])
    assert result.exit_code == 0
    assert "Schedule added" in result.output


def test_add_duplicate_exits_nonzero(runner):
    runner.invoke(schedule_group, ["add", "staging", "--cron", "0 * * * *"])
    result = runner.invoke(schedule_group, ["add", "staging", "--cron", "0 * * * *"])
    assert result.exit_code == 1
    assert "Error" in result.output


def test_list_empty(runner):
    result = runner.invoke(schedule_group, ["list"])
    assert result.exit_code == 0
    assert "No schedules" in result.output


def test_list_shows_entries(runner):
    runner.invoke(schedule_group, ["add", "prod", "--cron", "5 4 * * *", "--direction", "pull"])
    result = runner.invoke(schedule_group, ["list"])
    assert "prod" in result.output
    assert "pull" in result.output
    assert "5 4 * * *" in result.output


def test_remove_schedule(runner):
    runner.invoke(schedule_group, ["add", "prod", "--cron", "0 0 * * *"])
    result = runner.invoke(schedule_group, ["remove", "prod"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner):
    result = runner.invoke(schedule_group, ["remove", "ghost"])
    assert result.exit_code == 1


def test_disable_schedule(runner):
    runner.invoke(schedule_group, ["add", "prod", "--cron", "0 0 * * *"])
    result = runner.invoke(schedule_group, ["disable", "prod"])
    assert result.exit_code == 0
    assert "disabled" in result.output


def test_enable_schedule(runner):
    runner.invoke(schedule_group, ["add", "prod", "--cron", "0 0 * * *"])
    runner.invoke(schedule_group, ["disable", "prod"])
    result = runner.invoke(schedule_group, ["enable", "prod"])
    assert result.exit_code == 0
    assert "enabled" in result.output


def test_list_shows_disabled_status(runner):
    runner.invoke(schedule_group, ["add", "prod", "--cron", "0 0 * * *"])
    runner.invoke(schedule_group, ["disable", "prod"])
    result = runner.invoke(schedule_group, ["list"])
    assert "disabled" in result.output
