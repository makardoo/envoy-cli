"""Tests for envoy_cli.cli_confidence."""
import pytest
from click.testing import CliRunner
from envoy_cli.cli_confidence import confidence_group
from envoy_cli.confidence import set_confidence


@pytest.fixture()
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_HOME", str(tmp_path))
    import envoy_cli.cli_confidence as mod
    mod._BASE = str(tmp_path)
    return CliRunner(), tmp_path


def test_set_confidence(runner):
    cli, _ = runner
    result = cli.invoke(confidence_group, ["set", "prod", "high"])
    assert result.exit_code == 0
    assert "high" in result.output


def test_set_invalid_level_exits_nonzero(runner):
    cli, _ = runner
    result = cli.invoke(confidence_group, ["set", "prod", "extreme"])
    assert result.exit_code != 0


def test_get_confidence(runner):
    cli, base = runner
    set_confidence(str(base), "prod", "medium", note="ok")
    result = cli.invoke(confidence_group, ["get", "prod"])
    assert result.exit_code == 0
    assert "medium" in result.output
    assert "ok" in result.output


def test_get_missing_exits_nonzero(runner):
    cli, _ = runner
    result = cli.invoke(confidence_group, ["get", "ghost"])
    assert result.exit_code != 0


def test_remove_confidence(runner):
    cli, base = runner
    set_confidence(str(base), "dev", "low")
    result = cli.invoke(confidence_group, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_empty(runner):
    cli, _ = runner
    result = cli.invoke(confidence_group, ["list"])
    assert result.exit_code == 0
    assert "no confidence records" in result.output


def test_list_shows_entries(runner):
    cli, base = runner
    set_confidence(str(base), "prod", "high")
    set_confidence(str(base), "staging", "low")
    result = cli.invoke(confidence_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output
