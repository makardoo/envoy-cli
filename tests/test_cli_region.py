import pytest
from click.testing import CliRunner
from envoy_cli.cli_region import region_group


@pytest.fixture
def runner():
    return CliRunner()


def test_set_region(runner, tmp_path):
    result = runner.invoke(
        region_group, ["set", "prod", "us-east", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "us-east" in result.output


def test_set_invalid_region_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        region_group, ["set", "prod", "mars-1", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_get_region(runner, tmp_path):
    runner.invoke(region_group, ["set", "staging", "eu-west", "--base-dir", str(tmp_path)])
    result = runner.invoke(region_group, ["get", "staging", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "eu-west" in result.output


def test_get_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(region_group, ["get", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(region_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No region" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(region_group, ["set", "prod", "us-west", "--base-dir", str(tmp_path)])
    result = runner.invoke(region_group, ["list", "--base-dir", str(tmp_path)])
    assert "prod" in result.output
    assert "us-west" in result.output


def test_remove_region(runner, tmp_path):
    runner.invoke(region_group, ["set", "dev", "local", "--base-dir", str(tmp_path)])
    result = runner.invoke(region_group, ["remove", "dev", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    get_result = runner.invoke(region_group, ["get", "dev", "--base-dir", str(tmp_path)])
    assert get_result.exit_code != 0
