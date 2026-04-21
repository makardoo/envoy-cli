"""Tests for envoy_cli.visibility and envoy_cli.cli_visibility."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envoy_cli.visibility import (
    VisibilityError,
    set_visibility,
    get_visibility,
    remove_visibility,
    list_visibility,
)
from envoy_cli.cli_visibility import visibility_group


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


# --- unit tests ---

def test_set_and_get_visibility(base: Path) -> None:
    set_visibility(base, "prod", "private")
    assert get_visibility(base, "prod") == "private"


def test_set_creates_file(base: Path) -> None:
    set_visibility(base, "staging", "internal")
    assert (base / ".envoy" / "visibility.json").exists()


def test_get_missing_returns_default(base: Path) -> None:
    assert get_visibility(base, "nonexistent") == "private"


def test_set_invalid_level_raises(base: Path) -> None:
    with pytest.raises(VisibilityError, match="Invalid visibility level"):
        set_visibility(base, "prod", "secret")


def test_set_empty_name_raises(base: Path) -> None:
    with pytest.raises(VisibilityError, match="must not be empty"):
        set_visibility(base, "", "public")


def test_get_empty_name_raises(base: Path) -> None:
    with pytest.raises(VisibilityError, match="must not be empty"):
        get_visibility(base, "")


def test_remove_visibility(base: Path) -> None:
    set_visibility(base, "dev", "public")
    remove_visibility(base, "dev")
    assert get_visibility(base, "dev") == "private"


def test_remove_missing_raises(base: Path) -> None:
    with pytest.raises(VisibilityError, match="No visibility setting"):
        remove_visibility(base, "ghost")


def test_list_visibility(base: Path) -> None:
    set_visibility(base, "prod", "private")
    set_visibility(base, "staging", "internal")
    result = list_visibility(base)
    assert result == {"prod": "private", "staging": "internal"}


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_set_and_get(runner: CliRunner, base: Path) -> None:
    r = runner.invoke(visibility_group, ["set", "prod", "public", "--base-dir", str(base)])
    assert r.exit_code == 0
    assert "public" in r.output

    r = runner.invoke(visibility_group, ["get", "prod", "--base-dir", str(base)])
    assert r.exit_code == 0
    assert "public" in r.output


def test_cli_set_invalid_level_exits_nonzero(runner: CliRunner, base: Path) -> None:
    r = runner.invoke(visibility_group, ["set", "prod", "top-secret", "--base-dir", str(base)])
    assert r.exit_code != 0


def test_cli_list_empty(runner: CliRunner, base: Path) -> None:
    r = runner.invoke(visibility_group, ["list", "--base-dir", str(base)])
    assert r.exit_code == 0
    assert "No visibility" in r.output


def test_cli_remove(runner: CliRunner, base: Path) -> None:
    runner.invoke(visibility_group, ["set", "dev", "internal", "--base-dir", str(base)])
    r = runner.invoke(visibility_group, ["remove", "dev", "--base-dir", str(base)])
    assert r.exit_code == 0
    assert "removed" in r.output


def test_cli_remove_missing_exits_nonzero(runner: CliRunner, base: Path) -> None:
    r = runner.invoke(visibility_group, ["remove", "ghost", "--base-dir", str(base)])
    assert r.exit_code != 0
