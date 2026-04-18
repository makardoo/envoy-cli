"""CLI tests for webhook commands."""
import pytest
from click.testing import CliRunner
from envoy_cli.cli_webhook import webhook_group
from envoy_cli import webhook as wh_mod


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy_cli.cli_webhook._BASE", str(tmp_path))
    monkeypatch.setattr(wh_mod, "_BASE", str(tmp_path), raising=False)
    return CliRunner(), str(tmp_path)


def test_add_webhook(runner):
    cli_runner, base = runner
    result = cli_runner.invoke(webhook_group, ["add", "https://example.com", "--event", "push"])
    assert result.exit_code == 0
    assert "Registered" in result.output


def test_add_duplicate_exits_nonzero(runner):
    cli_runner, base = runner
    cli_runner.invoke(webhook_group, ["add", "https://example.com"])
    result = cli_runner.invoke(webhook_group, ["add", "https://example.com"])
    assert result.exit_code != 0


def test_list_empty(runner):
    cli_runner, base = runner
    result = cli_runner.invoke(webhook_group, ["list"])
    assert result.exit_code == 0
    assert "No webhooks" in result.output


def test_list_shows_entries(runner):
    cli_runner, base = runner
    cli_runner.invoke(webhook_group, ["add", "https://a.com", "--event", "push", "--label", "ci"])
    result = cli_runner.invoke(webhook_group, ["list"])
    assert "https://a.com" in result.output
    assert "ci" in result.output
    assert "push" in result.output


def test_remove_webhook(runner):
    cli_runner, base = runner
    cli_runner.invoke(webhook_group, ["add", "https://a.com"])
    result = cli_runner.invoke(webhook_group, ["remove", "https://a.com"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_exits_nonzero(runner):
    cli_runner, base = runner
    result = cli_runner.invoke(webhook_group, ["remove", "https://missing.com"])
    assert result.exit_code != 0
