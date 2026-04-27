"""Tests for envoy_cli.endorsement."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.endorsement import (
    EndorsementError,
    add_endorsement,
    get_endorsements,
    list_all_endorsements,
    remove_endorsement,
)
from envoy_cli.cli_endorsement import endorsement_group


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_add_and_get_endorsement(base):
    result = add_endorsement(base, "prod", "alice")
    assert "alice" in result
    assert get_endorsements(base, "prod") == ["alice"]


def test_add_creates_file(base, tmp_path):
    add_endorsement(base, "staging", "bob")
    assert (tmp_path / "endorsements.json").exists()


def test_add_duplicate_not_duplicated(base):
    add_endorsement(base, "prod", "alice")
    result = add_endorsement(base, "prod", "alice")
    assert result.count("alice") == 1


def test_add_multiple_endorsers(base):
    add_endorsement(base, "prod", "alice")
    add_endorsement(base, "prod", "bob")
    endorsers = get_endorsements(base, "prod")
    assert "alice" in endorsers
    assert "bob" in endorsers


def test_get_missing_returns_empty(base):
    assert get_endorsements(base, "nonexistent") == []


def test_remove_endorsement(base):
    add_endorsement(base, "prod", "alice")
    add_endorsement(base, "prod", "bob")
    result = remove_endorsement(base, "prod", "alice")
    assert "alice" not in result
    assert "bob" in result


def test_remove_missing_raises(base):
    with pytest.raises(EndorsementError):
        remove_endorsement(base, "prod", "ghost")


def test_add_empty_name_raises(base):
    with pytest.raises(EndorsementError):
        add_endorsement(base, "", "alice")


def test_add_empty_endorser_raises(base):
    with pytest.raises(EndorsementError):
        add_endorsement(base, "prod", "")


def test_list_all_endorsements(base):
    add_endorsement(base, "prod", "alice")
    add_endorsement(base, "staging", "bob")
    data = list_all_endorsements(base)
    assert "prod" in data
    assert "staging" in data


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_add(runner, tmp_path):
    result = runner.invoke(endorsement_group, ["add", "prod", "alice", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "alice" in result.output


def test_cli_remove(runner, tmp_path):
    add_endorsement(str(tmp_path), "prod", "alice")
    result = runner.invoke(endorsement_group, ["remove", "prod", "alice", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0


def test_cli_remove_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(endorsement_group, ["remove", "prod", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_cli_show_empty(runner, tmp_path):
    result = runner.invoke(endorsement_group, ["show", "prod", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No endorsements" in result.output


def test_cli_list_empty(runner, tmp_path):
    result = runner.invoke(endorsement_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No endorsements" in result.output
