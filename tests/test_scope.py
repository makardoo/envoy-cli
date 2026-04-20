"""Tests for envoy_cli.scope and envoy_cli.cli_scope."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.scope import (
    ScopeError,
    get_scope,
    list_all_scopes,
    list_by_scope,
    remove_scope,
    set_scope,
)
from envoy_cli.cli_scope import scope_group


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


# ── unit tests ────────────────────────────────────────────────────────────────

def test_set_and_get_scope(base):
    set_scope(base, "app", "production")
    assert get_scope(base, "app") == "production"


def test_set_creates_file(base):
    from pathlib import Path
    set_scope(base, "app", "staging")
    assert (Path(base) / "scopes.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(ScopeError, match="No scope set"):
        get_scope(base, "missing")


def test_set_empty_name_raises(base):
    with pytest.raises(ScopeError):
        set_scope(base, "", "local")


def test_set_invalid_scope_raises(base):
    with pytest.raises(ScopeError, match="Invalid scope"):
        set_scope(base, "app", "unknown")


def test_remove_scope(base):
    set_scope(base, "app", "local")
    remove_scope(base, "app")
    with pytest.raises(ScopeError):
        get_scope(base, "app")


def test_remove_missing_raises(base):
    with pytest.raises(ScopeError):
        remove_scope(base, "ghost")


def test_list_by_scope(base):
    set_scope(base, "a", "staging")
    set_scope(base, "b", "production")
    set_scope(base, "c", "staging")
    assert list_by_scope(base, "staging") == ["a", "c"]


def test_list_by_invalid_scope_raises(base):
    with pytest.raises(ScopeError, match="Invalid scope"):
        list_by_scope(base, "nope")


def test_list_all_scopes(base):
    set_scope(base, "x", "global")
    set_scope(base, "y", "local")
    data = list_all_scopes(base)
    assert data == {"x": "global", "y": "local"}


# ── CLI tests ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_scope(runner, base):
    result = runner.invoke(scope_group, ["set", "app", "production", "--base-dir", base])
    assert result.exit_code == 0
    assert "production" in result.output


def test_cli_set_invalid_scope_exits_nonzero(runner, base):
    result = runner.invoke(scope_group, ["set", "app", "nope", "--base-dir", base])
    assert result.exit_code != 0


def test_cli_get_scope(runner, base):
    set_scope(base, "app", "staging")
    result = runner.invoke(scope_group, ["get", "app", "--base-dir", base])
    assert result.exit_code == 0
    assert "staging" in result.output


def test_cli_get_missing_exits_nonzero(runner, base):
    result = runner.invoke(scope_group, ["get", "ghost", "--base-dir", base])
    assert result.exit_code != 0


def test_cli_list_all(runner, base):
    set_scope(base, "a", "local")
    set_scope(base, "b", "global")
    result = runner.invoke(scope_group, ["list", "--base-dir", base])
    assert result.exit_code == 0
    assert "a: local" in result.output
    assert "b: global" in result.output


def test_cli_list_by_scope(runner, base):
    set_scope(base, "a", "local")
    set_scope(base, "b", "staging")
    result = runner.invoke(scope_group, ["list", "--scope", "local", "--base-dir", base])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "b" not in result.output
