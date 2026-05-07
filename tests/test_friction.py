"""Tests for envoy_cli.friction."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.friction import (
    FrictionError,
    set_friction,
    get_friction,
    remove_friction,
    list_friction,
)
from envoy_cli.cli_friction import friction_group


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_friction(base):
    set_friction(base, "prod", "high", "many required keys")
    rec = get_friction(base, "prod")
    assert rec["level"] == "high"
    assert rec["reason"] == "many required keys"


def test_set_creates_file(base, tmp_path):
    set_friction(base, "staging", "low")
    assert (tmp_path / "friction.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(FrictionError, match="no friction record"):
        get_friction(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(FrictionError, match="must not be empty"):
        set_friction(base, "", "low")


def test_set_invalid_level_raises(base):
    with pytest.raises(FrictionError, match="invalid friction level"):
        set_friction(base, "dev", "extreme")


def test_remove_friction(base):
    set_friction(base, "dev", "none")
    remove_friction(base, "dev")
    with pytest.raises(FrictionError):
        get_friction(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(FrictionError, match="no friction record"):
        remove_friction(base, "ghost")


def test_list_friction_empty(base):
    assert list_friction(base) == []


def test_list_friction_returns_all(base):
    set_friction(base, "prod", "critical", "very complex")
    set_friction(base, "dev", "none")
    records = list_friction(base)
    names = [r["name"] for r in records]
    assert "prod" in names
    assert "dev" in names


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_friction(runner, tmp_path):
    result = runner.invoke(
        friction_group, ["set", "prod", "high", "--reason", "complex", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "high" in result.output


def test_cli_set_invalid_level_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        friction_group, ["set", "prod", "extreme", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_cli_get_friction(runner, tmp_path):
    set_friction(str(tmp_path), "staging", "medium", "some issues")
    result = runner.invoke(friction_group, ["get", "staging", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "medium" in result.output
    assert "some issues" in result.output


def test_cli_get_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(friction_group, ["get", "ghost", "--base-dir", str(tmp_path)])
    assert result.exit_code != 0


def test_cli_list_empty(runner, tmp_path):
    result = runner.invoke(friction_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "no friction" in result.output
