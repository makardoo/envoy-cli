"""Tests for envoy_cli.obsolescence and cli_obsolescence."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.obsolescence import (
    ObsolescenceError,
    get_obsolescence,
    list_obsolete,
    mark_obsolete,
    unmark_obsolete,
)
from envoy_cli.cli_obsolescence import obsolescence_group


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


# --- unit tests ---

def test_mark_and_get(base):
    entry = mark_obsolete(base, "prod", reason="superseded")
    assert entry["obsolete"] is True
    assert entry["reason"] == "superseded"
    assert "marked_at" in entry
    fetched = get_obsolescence(base, "prod")
    assert fetched == entry


def test_mark_creates_file(base, tmp_path):
    mark_obsolete(base, "staging")
    assert (tmp_path / "obsolescence.json").exists()


def test_mark_empty_reason(base):
    entry = mark_obsolete(base, "dev")
    assert entry["reason"] == ""


def test_get_missing_raises(base):
    with pytest.raises(ObsolescenceError, match="no obsolescence record"):
        get_obsolescence(base, "ghost")


def test_mark_empty_name_raises(base):
    with pytest.raises(ObsolescenceError, match="must not be empty"):
        mark_obsolete(base, "")


def test_unmark_removes_entry(base):
    mark_obsolete(base, "prod")
    unmark_obsolete(base, "prod")
    with pytest.raises(ObsolescenceError):
        get_obsolescence(base, "prod")


def test_unmark_not_marked_raises(base):
    with pytest.raises(ObsolescenceError, match="not marked as obsolete"):
        unmark_obsolete(base, "prod")


def test_list_obsolete_returns_sorted(base):
    mark_obsolete(base, "z-env")
    mark_obsolete(base, "a-env")
    assert list_obsolete(base) == ["a-env", "z-env"]


def test_list_empty(base):
    assert list_obsolete(base) == []


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_mark(runner, base):
    result = runner.invoke(obsolescence_group, ["mark", "prod", "--base-dir", base])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_cli_mark_with_reason(runner, base):
    result = runner.invoke(
        obsolescence_group,
        ["mark", "prod", "--reason", "old", "--base-dir", base],
    )
    assert result.exit_code == 0


def test_cli_get(runner, base):
    mark_obsolete(base, "staging", reason="archived")
    result = runner.invoke(obsolescence_group, ["get", "staging", "--base-dir", base])
    assert result.exit_code == 0
    assert "archived" in result.output


def test_cli_get_missing_exits_nonzero(runner, base):
    result = runner.invoke(obsolescence_group, ["get", "missing", "--base-dir", base])
    assert result.exit_code != 0


def test_cli_unmark(runner, base):
    mark_obsolete(base, "dev")
    result = runner.invoke(obsolescence_group, ["unmark", "dev", "--base-dir", base])
    assert result.exit_code == 0
    assert "dev" in result.output


def test_cli_list(runner, base):
    mark_obsolete(base, "alpha")
    mark_obsolete(base, "beta")
    result = runner.invoke(obsolescence_group, ["list", "--base-dir", base])
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output
