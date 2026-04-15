"""Tests for envoy_cli.diff module."""

import pytest
from envoy_cli.diff import parse_env_dict, diff_envs, format_diff


OLD_ENV = """DB_HOST=localhost
DB_PORT=5432
SECRET=old_secret
DEBUG=true
"""

NEW_ENV = """DB_HOST=localhost
DB_PORT=5433
SECRET=new_secret
API_KEY=abc123
"""


def test_parse_env_dict_basic():
    content = "FOO=bar\nBAZ=qux\n"
    result = parse_env_dict(content)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_dict_ignores_comments_and_blanks():
    content = "# comment\n\nFOO=bar\n"
    result = parse_env_dict(content)
    assert result == {"FOO": "bar"}


def test_parse_env_dict_handles_equals_in_value():
    content = "TOKEN=abc=def==\n"
    result = parse_env_dict(content)
    assert result["TOKEN"] == "abc=def=="


def test_diff_envs_detects_added():
    diff = diff_envs(OLD_ENV, NEW_ENV)
    keys = [k for k, _ in diff["added"]]
    assert "API_KEY" in keys


def test_diff_envs_detects_removed():
    diff = diff_envs(OLD_ENV, NEW_ENV)
    keys = [k for k, _ in diff["removed"]]
    assert "DEBUG" in keys


def test_diff_envs_detects_changed():
    diff = diff_envs(OLD_ENV, NEW_ENV)
    keys = [k for k, _, __ in diff["changed"]]
    assert "DB_PORT" in keys
    assert "SECRET" in keys


def test_diff_envs_detects_unchanged():
    diff = diff_envs(OLD_ENV, NEW_ENV)
    keys = [k for k, _ in diff["unchanged"]]
    assert "DB_HOST" in keys


def test_diff_envs_identical_content():
    diff = diff_envs(OLD_ENV, OLD_ENV)
    assert diff["added"] == []
    assert diff["removed"] == []
    assert diff["changed"] == []
    assert len(diff["unchanged"]) == 4


def test_format_diff_masks_values_by_default():
    diff = diff_envs(OLD_ENV, NEW_ENV)
    output = format_diff(diff)
    assert "***" in output
    assert "old_secret" not in output
    assert "new_secret" not in output


def test_format_diff_shows_values_when_unmasked():
    diff = diff_envs(OLD_ENV, NEW_ENV)
    output = format_diff(diff, mask_values=False)
    assert "abc123" in output


def test_format_diff_no_differences():
    diff = diff_envs(OLD_ENV, OLD_ENV)
    output = format_diff(diff)
    assert output == "No differences found."


def test_format_diff_summary_line():
    diff = diff_envs(OLD_ENV, NEW_ENV)
    output = format_diff(diff)
    first_line = output.splitlines()[0]
    assert "+1" in first_line
    assert "-1" in first_line
    assert "~2" in first_line
