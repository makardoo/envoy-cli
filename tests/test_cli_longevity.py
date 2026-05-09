"""Tests for envoy_cli.cli_longevity."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envoy_cli.cli_longevity import longevity_group
from envoy_cli.longevity import record_creation


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def _invoke(runner: CliRunner, base: Path, *args: str):
    return runner.invoke(longevity_group, ["--base-dir", str(base), *args])


def test_record_cmd(runner: CliRunner, base: Path) -> None:
    result = _invoke(runner, base, "record", "prod")
    assert result.exit_code == 0
    assert "prod" in result.output


def test_record_cmd_idempotent(runner: CliRunner, base: Path) -> None:
    r1 = _invoke(runner, base, "record", "prod")
    r2 = _invoke(runner, base, "record", "prod")
    assert r1.exit_code == 0
    assert r2.exit_code == 0
    # Both should report the same timestamp
    ts1 = r1.output.strip().split()[-1]
    ts2 = r2.output.strip().split()[-1]
    assert ts1 == ts2


def test_show_cmd(runner: CliRunner, base: Path) -> None:
    record_creation(base, "staging")
    result = _invoke(runner, base, "show", "staging")
    assert result.exit_code == 0
    assert "staging" in result.output
    assert "age_days" in result.output


def test_show_missing_exits_nonzero(runner: CliRunner, base: Path) -> None:
    result = _invoke(runner, base, "show", "ghost")
    assert result.exit_code != 0


def test_remove_cmd(runner: CliRunner, base: Path) -> None:
    record_creation(base, "dev")
    result = _invoke(runner, base, "remove", "dev")
    assert result.exit_code == 0
    show = _invoke(runner, base, "show", "dev")
    assert show.exit_code != 0


def test_remove_missing_exits_nonzero(runner: CliRunner, base: Path) -> None:
    result = _invoke(runner, base, "remove", "ghost")
    assert result.exit_code != 0


def test_list_empty(runner: CliRunner, base: Path) -> None:
    result = _invoke(runner, base, "list")
    assert result.exit_code == 0
    assert "No longevity" in result.output


def test_list_shows_entries(runner: CliRunner, base: Path) -> None:
    record_creation(base, "alpha")
    record_creation(base, "beta")
    result = _invoke(runner, base, "list")
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output
