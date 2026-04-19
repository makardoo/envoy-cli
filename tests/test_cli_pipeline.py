import pytest
from click.testing import CliRunner
from envoy_cli.cli_pipeline import pipeline_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_create_pipeline(runner, base):
    result = runner.invoke(pipeline_group, ["create", "deploy", "validate", "push", "--base-dir", base])
    assert result.exit_code == 0
    assert "created" in result.output


def test_create_duplicate_exits_nonzero(runner, base):
    runner.invoke(pipeline_group, ["create", "p", "a", "--base-dir", base])
    result = runner.invoke(pipeline_group, ["create", "p", "b", "--base-dir", base])
    assert result.exit_code != 0


def test_show_pipeline(runner, base):
    runner.invoke(pipeline_group, ["create", "p", "step1", "step2", "--base-dir", base])
    result = runner.invoke(pipeline_group, ["show", "p", "--base-dir", base])
    assert result.exit_code == 0
    assert "step1" in result.output
    assert "step2" in result.output


def test_show_missing_exits_nonzero(runner, base):
    result = runner.invoke(pipeline_group, ["show", "ghost", "--base-dir", base])
    assert result.exit_code != 0


def test_list_empty(runner, base):
    result = runner.invoke(pipeline_group, ["list", "--base-dir", base])
    assert result.exit_code == 0
    assert "No pipelines" in result.output


def test_list_shows_entries(runner, base):
    runner.invoke(pipeline_group, ["create", "a", "x", "--base-dir", base])
    runner.invoke(pipeline_group, ["create", "b", "y", "--base-dir", base])
    result = runner.invoke(pipeline_group, ["list", "--base-dir", base])
    assert "a" in result.output
    assert "b" in result.output


def test_delete_pipeline(runner, base):
    runner.invoke(pipeline_group, ["create", "p", "x", "--base-dir", base])
    result = runner.invoke(pipeline_group, ["delete", "p", "--base-dir", base])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_update_pipeline(runner, base):
    runner.invoke(pipeline_group, ["create", "p", "old", "--base-dir", base])
    result = runner.invoke(pipeline_group, ["update", "p", "new1", "new2", "--base-dir", base])
    assert result.exit_code == 0
    assert "updated" in result.output
