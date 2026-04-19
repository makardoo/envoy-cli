"""Tests for envoy_cli.cli_version."""
import pytest
from click.testing import CliRunner
from envoy_cli.cli_version import version_group
from envoy_cli.version import record_version
import os


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    import envoy_cli.cli_version as cv
    cv._BASE_DIR = str(tmp_path)
    return CliRunner(), str(tmp_path)


def test_record_cmd(runner):
    r, base = runner
    result = r.invoke(version_group, ["record", "prod", "KEY=val", "-m", "initial"])
    assert result.exit_code == 0
    assert "version 1" in result.output


def test_list_empty(runner):
    r, base = runner
    result = r.invoke(version_group, ["list", "prod"])
    assert result.exit_code == 0
    assert "No versions" in result.output


def test_list_shows_entries(runner):
    r, base = runner
    record_version(base, "prod", "A=1", "first")
    record_version(base, "prod", "A=2", "second")
    result = r.invoke(version_group, ["list", "prod"])
    assert "v1" in result.output
    assert "v2" in result.output
    assert "first" in result.output


def test_show_version(runner):
    r, base = runner
    record_version(base, "prod", "KEY=secret")
    result = r.invoke(version_group, ["show", "prod", "1"])
    assert result.exit_code == 0
    assert "KEY=secret" in result.output


def test_show_missing_exits_nonzero(runner):
    r, base = runner
    result = r.invoke(version_group, ["show", "prod", "99"])
    assert result.exit_code != 0


def test_clear_cmd(runner):
    r, base = runner
    record_version(base, "prod", "A=1")
    result = r.invoke(version_group, ["clear", "prod"])
    assert result.exit_code == 0
    assert "Cleared" in result.output
    result2 = r.invoke(version_group, ["list", "prod"])
    assert "No versions" in result2.output
