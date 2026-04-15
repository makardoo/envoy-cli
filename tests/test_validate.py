"""Tests for envoy_cli.validate and cli_validate."""

import pytest
from click.testing import CliRunner
from envoy_cli.validate import validate_env_content, validate_against_schema
from envoy_cli.cli_validate import validate_group
from envoy_cli.storage import save_env


# ---------------------------------------------------------------------------
# validate_env_content
# ---------------------------------------------------------------------------

def test_valid_content_returns_no_issues():
    content = "KEY=value\nOTHER=123\n"
    result = validate_env_content(content)
    assert result.valid is True
    assert result.issues == []


def test_detects_missing_equals():
    content = "BADLINE\nGOOD=ok\n"
    result = validate_env_content(content)
    assert result.valid is False
    assert any("invalid format" in i.message for i in result.issues)


def test_detects_empty_key():
    content = "=value\n"
    result = validate_env_content(content)
    assert result.valid is False
    assert any("empty key" in i.message for i in result.issues)


def test_detects_duplicate_key():
    content = "FOO=bar\nFOO=baz\n"
    result = validate_env_content(content)
    assert result.valid is True  # duplicate is a warning, not an error
    assert any("duplicate" in i.message for i in result.issues)


def test_detects_empty_value():
    content = "FOO=\n"
    result = validate_env_content(content)
    assert result.valid is True
    assert any("empty value" in i.message for i in result.issues)


def test_ignores_comments_and_blank_lines():
    content = "# comment\n\nKEY=val\n"
    result = validate_env_content(content)
    assert result.valid is True
    assert result.issues == []


# ---------------------------------------------------------------------------
# validate_against_schema
# ---------------------------------------------------------------------------

def test_schema_passes_when_all_keys_present():
    content = "DB_URL=postgres://localhost\nSECRET=abc\n"
    result = validate_against_schema(content, ["DB_URL", "SECRET"])
    assert result.valid is True


def test_schema_fails_when_key_missing():
    content = "DB_URL=postgres://localhost\n"
    result = validate_against_schema(content, ["DB_URL", "SECRET"])
    assert result.valid is False
    assert any("SECRET" in i.message for i in result.issues)


# ---------------------------------------------------------------------------
# CLI: check-file
# ---------------------------------------------------------------------------

def test_cli_check_file_valid(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\nOTHER=123\n")
    runner = CliRunner()
    result = runner.invoke(validate_group, ["check-file", str(env_file)])
    assert result.exit_code == 0
    assert "valid" in result.output


def test_cli_check_file_with_errors(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("BADLINE\n")
    runner = CliRunner()
    result = runner.invoke(validate_group, ["check-file", str(env_file)])
    assert result.exit_code == 1


def test_cli_check_file_require_missing_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PRESENT=yes\n")
    runner = CliRunner()
    result = runner.invoke(validate_group, ["check-file", str(env_file), "--require", "MISSING"])
    assert result.exit_code == 1
    assert "MISSING" in result.output


# ---------------------------------------------------------------------------
# CLI: check (stored env)
# ---------------------------------------------------------------------------

def test_cli_check_stored_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_DIR", str(tmp_path))
    save_env("myapp", "KEY=value\n", "secret")
    runner = CliRunner()
    result = runner.invoke(validate_group, ["check", "myapp"], input="secret\n")
    assert result.exit_code == 0
    assert "valid" in result.output


def test_cli_check_stored_env_not_found(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_DIR", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(validate_group, ["check", "ghost"], input="secret\n")
    assert result.exit_code == 1
