"""Tests for the audit CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch

from envoy_cli.cli_audit import audit_group
from envoy_cli.audit import append_audit_entry


@pytest.fixture
def isolated_audit(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_DIR", str(tmp_path))
    with patch("envoy_cli.cli_audit.get_env_dir", return_value=str(tmp_path)):
        yield tmp_path


def test_show_log_empty(isolated_audit):
    runner = CliRunner()
    result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "No audit log entries found" in result.output


def test_show_log_displays_entries(isolated_audit):
    append_audit_entry(str(isolated_audit), "set", "myapp", "local", user="bob")
    append_audit_entry(str(isolated_audit), "push", "myapp", "staging", user="bob")
    runner = CliRunner()
    result = runner.invoke(audit_group, ["log"])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "push" in result.output
    assert "myapp" in result.output
    assert "bob" in result.output


def test_show_log_filter_by_action(isolated_audit):
    append_audit_entry(str(isolated_audit), "set", "myapp", "local")
    append_audit_entry(str(isolated_audit), "push", "myapp", "staging")
    runner = CliRunner()
    result = runner.invoke(audit_group, ["log", "--action", "set"])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "push" not in result.output


def test_show_log_filter_by_env_name(isolated_audit):
    append_audit_entry(str(isolated_audit), "set", "app1", "local")
    append_audit_entry(str(isolated_audit), "set", "app2", "local")
    runner = CliRunner()
    result = runner.invoke(audit_group, ["log", "--env", "app1"])
    assert result.exit_code == 0
    assert "app1" in result.output
    assert "app2" not in result.output


def test_show_log_limit(isolated_audit):
    for i in range(10):
        append_audit_entry(str(isolated_audit), "set", f"app{i}", "local")
    runner = CliRunner()
    result = runner.invoke(audit_group, ["log", "--limit", "3"])
    assert result.exit_code == 0
    lines = [l for l in result.output.splitlines() if "app" in l]
    assert len(lines) == 3


def test_clear_log_removes_file(isolated_audit):
    append_audit_entry(str(isolated_audit), "set", "myapp", "local")
    runner = CliRunner()
    result = runner.invoke(audit_group, ["clear"], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    from envoy_cli.audit import get_audit_log_path
    assert not get_audit_log_path(str(isolated_audit)).exists()


def test_clear_log_no_file(isolated_audit):
    runner = CliRunner()
    result = runner.invoke(audit_group, ["clear"], input="y\n")
    assert result.exit_code == 0
    assert "No audit log" in result.output
