"""Tests for envoy_cli.cli_resilience."""
import pytest
from click.testing import CliRunner
from envoy_cli.cli_resilience import resilience_group


@pytest.fixture()
def runner():
    return CliRunner()


def test_set_resilience(runner, tmp_path):
    result = runner.invoke(
        resilience_group,
        ["set", "prod", "robust", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "robust" in result.output


def test_set_invalid_level_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        resilience_group,
        ["set", "prod", "invincible", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code != 0


def test_get_resilience(runner, tmp_path):
    runner.invoke(
        resilience_group,
        ["set", "staging", "moderate", "--base-dir", str(tmp_path)],
    )
    result = runner.invoke(
        resilience_group,
        ["get", "staging", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "moderate" in result.output


def test_get_missing_returns_default(runner, tmp_path):
    result = runner.invoke(
        resilience_group,
        ["get", "unknown", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "fragile" in result.output


def test_remove_resilience(runner, tmp_path):
    runner.invoke(
        resilience_group,
        ["set", "dev", "hardened", "--base-dir", str(tmp_path)],
    )
    result = runner.invoke(
        resilience_group,
        ["remove", "dev", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        resilience_group,
        ["remove", "ghost", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(
        resilience_group,
        ["list", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "No resilience records" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(
        resilience_group,
        ["set", "prod", "hardened", "--base-dir", str(tmp_path)],
    )
    result = runner.invoke(
        resilience_group,
        ["list", "--base-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "hardened" in result.output
