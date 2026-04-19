import pytest
from click.testing import CliRunner
from envoy_cli.cli_workflow import workflow_group
import envoy_cli.cli_workflow as cli_wf_module


@pytest.fixture
def runner(tmp_path):
    cli_wf_module._BASE = str(tmp_path)
    return CliRunner()


def test_create_workflow(runner):
    result = runner.invoke(workflow_group, ["create", "deploy", "validate", "push"])
    assert result.exit_code == 0
    assert "deploy" in result.output
    assert "2 step" in result.output


def test_create_duplicate_exits_nonzero(runner):
    runner.invoke(workflow_group, ["create", "deploy", "push"])
    result = runner.invoke(workflow_group, ["create", "deploy", "push"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_show_workflow(runner):
    runner.invoke(workflow_group, ["create", "ci", "lint", "test"])
    result = runner.invoke(workflow_group, ["show", "ci"])
    assert result.exit_code == 0
    assert "lint" in result.output
    assert "test" in result.output


def test_show_missing_exits_nonzero(runner):
    result = runner.invoke(workflow_group, ["show", "ghost"])
    assert result.exit_code != 0


def test_update_workflow(runner):
    runner.invoke(workflow_group, ["create", "deploy", "push"])
    result = runner.invoke(workflow_group, ["update", "deploy", "validate", "push"])
    assert result.exit_code == 0
    assert "Updated" in result.output


def test_delete_workflow(runner):
    runner.invoke(workflow_group, ["create", "deploy", "push"])
    result = runner.invoke(workflow_group, ["delete", "deploy"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_list_empty(runner):
    result = runner.invoke(workflow_group, ["list"])
    assert result.exit_code == 0
    assert "No workflows" in result.output


def test_list_shows_entries(runner):
    runner.invoke(workflow_group, ["create", "a", "step1"])
    runner.invoke(workflow_group, ["create", "b", "step2", "step3"])
    result = runner.invoke(workflow_group, ["list"])
    assert "a" in result.output
    assert "b" in result.output
