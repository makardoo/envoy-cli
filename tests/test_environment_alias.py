"""Tests for envoy_cli.environment_alias and its CLI."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.environment_alias import (
    EnvAliasError,
    list_env_aliases,
    remove_env_alias,
    resolve_env_alias,
    set_env_alias,
)
from envoy_cli.cli_environment_alias import env_alias_group


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


# --- unit tests ---

def test_set_and_resolve(base):
    set_env_alias(base, "prod", "production")
    assert resolve_env_alias(base, "prod") == "production"


def test_set_creates_file(base, tmp_path):
    set_env_alias(base, "stg", "staging")
    assert (tmp_path / "env_aliases.json").exists()


def test_resolve_missing_raises(base):
    with pytest.raises(EnvAliasError, match="not found"):
        resolve_env_alias(base, "ghost")


def test_set_empty_alias_raises(base):
    with pytest.raises(EnvAliasError, match="empty"):
        set_env_alias(base, "", "production")


def test_set_empty_env_name_raises(base):
    with pytest.raises(EnvAliasError, match="empty"):
        set_env_alias(base, "prod", "")


def test_overwrite_alias(base):
    set_env_alias(base, "prod", "production")
    set_env_alias(base, "prod", "prod-v2")
    assert resolve_env_alias(base, "prod") == "prod-v2"


def test_remove_alias(base):
    set_env_alias(base, "dev", "development")
    remove_env_alias(base, "dev")
    with pytest.raises(EnvAliasError):
        resolve_env_alias(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(EnvAliasError, match="not found"):
        remove_env_alias(base, "nope")


def test_list_empty(base):
    assert list_env_aliases(base) == []


def test_list_returns_sorted(base):
    set_env_alias(base, "zz", "z-env")
    set_env_alias(base, "aa", "a-env")
    entries = list_env_aliases(base)
    assert entries[0]["alias"] == "aa"
    assert entries[1]["alias"] == "zz"


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_and_get(runner, tmp_path):
    base = str(tmp_path)
    result = runner.invoke(env_alias_group, ["set", "prod", "production", "--base-dir", base])
    assert result.exit_code == 0
    result = runner.invoke(env_alias_group, ["get", "prod", "--base-dir", base])
    assert result.exit_code == 0
    assert "production" in result.output


def test_cli_get_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(env_alias_group, ["get", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_cli_remove(runner, tmp_path):
    base = str(tmp_path)
    runner.invoke(env_alias_group, ["set", "dev", "development", "--base-dir", base])
    result = runner.invoke(env_alias_group, ["remove", "dev", "--base-dir", base])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_list_empty(runner, tmp_path):
    result = runner.invoke(env_alias_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_cli_list_shows_entries(runner, tmp_path):
    base = str(tmp_path)
    runner.invoke(env_alias_group, ["set", "prod", "production", "--base-dir", base])
    result = runner.invoke(env_alias_group, ["list", "--base-dir", base])
    assert "prod" in result.output
    assert "production" in result.output
