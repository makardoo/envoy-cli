"""Tests for envoy_cli.import_env and envoy_cli.cli_import."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from envoy_cli.import_env import (
    detect_format,
    parse_dotenv,
    import_from_file,
    import_from_string,
    merge_envs,
)
from envoy_cli.cli_import import import_group
from envoy_cli import storage


# --- Unit tests for import_env module ---

def test_detect_format_dotenv():
    content = "KEY=value\nOTHER=123\n"
    assert detect_format(content) == "dotenv"


def test_detect_format_shell():
    content = "export KEY=value\nexport OTHER=123\n"
    assert detect_format(content) == "shell"


def test_parse_dotenv_basic():
    content = "FOO=bar\nBAZ=qux\n"
    result = parse_dotenv(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_dotenv_strips_quotes():
    content = 'FOO="hello world"\nBAR=\'single\'\n'
    result = parse_dotenv(content)
    assert result["FOO"] == "hello world"
    assert result["BAR"] == "single"


def test_parse_dotenv_ignores_comments_and_blanks():
    content = "# comment\n\nFOO=bar\n"
    result = parse_dotenv(content)
    assert result == {"FOO": "bar"}


def test_parse_dotenv_handles_export_prefix():
    content = "export FOO=bar\nexport BAZ=qux\n"
    result = parse_dotenv(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_import_from_string_dotenv():
    content = "A=1\nB=2\n"
    result = import_from_string(content)
    assert result == {"A": "1", "B": "2"}


def test_import_from_string_invalid_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        import_from_string("A=1", fmt="xml")


def test_import_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        import_from_file("/nonexistent/path/.env")


def test_import_from_file_reads_content(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET=abc\nPORT=8080\n")
    result = import_from_file(str(env_file))
    assert result == {"SECRET": "abc", "PORT": "8080"}


def test_merge_envs_override():
    base = {"A": "1", "B": "2"}
    override = {"B": "99", "C": "3"}
    result = merge_envs(base, override, strategy="override")
    assert result == {"A": "1", "B": "99", "C": "3"}


def test_merge_envs_keep():
    base = {"A": "1", "B": "2"}
    override = {"B": "99", "C": "3"}
    result = merge_envs(base, override, strategy="keep")
    assert result["B"] == "2"  # base wins
    assert result["C"] == "3"


def test_merge_envs_invalid_strategy():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs({}, {}, strategy="unknown")


# --- CLI integration test ---

@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "get_env_dir", lambda: str(tmp_path))
    return tmp_path


def test_cli_import_file(isolated_store, tmp_path):
    env_file = tmp_path / "sample.env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\n")
    runner = CliRunner()
    result = runner.invoke(
        import_group,
        ["file", "myapp", str(env_file), "--passphrase", "secret123"],
    )
    assert result.exit_code == 0, result.output
    assert "2 key(s)" in result.output
    assert "myapp" in result.output


def test_cli_import_file_not_found(isolated_store):
    runner = CliRunner()
    result = runner.invoke(
        import_group,
        ["file", "myapp", "/no/such/file.env", "--passphrase", "secret"],
    )
    assert result.exit_code != 0
    assert "Error" in result.output
