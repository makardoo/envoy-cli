import pytest
from click.testing import CliRunner
from envoy_cli.cli_tier import tier_group


@pytest.fixture
def runner():
    return CliRunner()


def test_set_tier(runner, tmp_path):
    result = runner.invoke(tier_group, ["set", "prod", "enterprise", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "enterprise" in result.output


def test_set_invalid_tier_exits_nonzero(runner, tmp_path):
    result = runner.invoke(tier_group, ["set", "prod", "invalid", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_get_tier(runner, tmp_path):
    runner.invoke(tier_group, ["set", "prod", "pro", "--base-dir", str(tmp_path)])
    result = runner.invoke(tier_group, ["get", "prod", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "pro" in result.output


def test_get_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(tier_group, ["get", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code == 1


def test_remove_tier(runner, tmp_path):
    runner.invoke(tier_group, ["set", "dev", "free", "--base-dir", str(tmp_path)])
    result = runner.invoke(tier_group, ["remove", "dev", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(tier_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No tiers" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(tier_group, ["set", "prod", "enterprise", "--base-dir", str(tmp_path)])
    runner.invoke(tier_group, ["set", "staging", "pro", "--base-dir", str(tmp_path)])
    result = runner.invoke(tier_group, ["list", "--base-dir", str(tmp_path)])
    assert "prod" in result.output
    assert "enterprise" in result.output
    assert "staging" in result.output
