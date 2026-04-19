"""CLI tests for metadata commands."""
import pytest
from click.testing import CliRunner
from envoy_cli.cli_metadata import metadata_group
import envoy_cli.cli_metadata as cli_meta_mod


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_meta_mod, "_BASE", str(tmp_path))
    return CliRunner()


def test_set_metadata(runner):
    result = runner.invoke(metadata_group, ["set", "prod", "owner", "alice"])
    assert result.exit_code == 0
    assert "set" in result.output


def test_get_metadata(runner):
    runner.invoke(metadata_group, ["set", "prod", "owner", "alice"])
    result = runner.invoke(metadata_group, ["get", "prod", "owner"])
    assert result.exit_code == 0
    assert "alice" in result.output


def test_get_missing_exits_nonzero(runner):
    result = runner.invoke(metadata_group, ["get", "prod", "missing"])
    assert result.exit_code != 0


def test_remove_metadata(runner):
    runner.invoke(metadata_group, ["set", "prod", "owner", "alice"])
    result = runner.invoke(metadata_group, ["remove", "prod", "owner"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_missing_exits_nonzero(runner):
    result = runner.invoke(metadata_group, ["remove", "prod", "ghost"])
    assert result.exit_code != 0


def test_show_metadata(runner):
    runner.invoke(metadata_group, ["set", "prod", "owner", "alice"])
    result = runner.invoke(metadata_group, ["show", "prod"])
    assert result.exit_code == 0
    assert "owner=alice" in result.output


def test_show_empty(runner):
    result = runner.invoke(metadata_group, ["show", "prod"])
    assert result.exit_code == 0
    assert "No metadata" in result.output


def test_list_all(runner):
    runner.invoke(metadata_group, ["set", "prod", "owner", "alice"])
    runner.invoke(metadata_group, ["set", "staging", "team", "ops"])
    result = runner.invoke(metadata_group, ["list"])
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output


def test_list_empty(runner):
    result = runner.invoke(metadata_group, ["list"])
    assert result.exit_code == 0
    assert "No metadata" in result.output
