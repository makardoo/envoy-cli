"""Tests for envoy_cli.cli_velocity."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envoy_cli.cli_velocity import velocity_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def _invoke(runner: CliRunner, base: Path, *args: str):
    with patch("envoy_cli.cli_velocity._base_dir", return_value=base):
        return runner.invoke(velocity_group, list(args))


def test_record_cmd(runner: CliRunner, base: Path) -> None:
    result = _invoke(runner, base, "record", "staging")
    assert result.exit_code == 0
    assert "staging" in result.output


def test_show_cmd_no_changes(runner: CliRunner, base: Path) -> None:
    result = _invoke(runner, base, "show", "staging")
    assert result.exit_code == 0
    assert "total" in result.output
    assert "never" in result.output


def test_show_cmd_after_record(runner: CliRunner, base: Path) -> None:
    _invoke(runner, base, "record", "prod")
    result = _invoke(runner, base, "show", "prod")
    assert result.exit_code == 0
    assert "total     : 1" in result.output


def test_list_cmd_empty(runner: CliRunner, base: Path) -> None:
    result = _invoke(runner, base, "list", "dev")
    assert result.exit_code == 0
    assert "No changes" in result.output


def test_list_cmd_shows_timestamps(runner: CliRunner, base: Path) -> None:
    _invoke(runner, base, "record", "dev")
    _invoke(runner, base, "record", "dev")
    result = _invoke(runner, base, "list", "dev")
    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l]
    assert len(lines) == 2


def test_clear_cmd(runner: CliRunner, base: Path) -> None:
    _invoke(runner, base, "record", "dev")
    result = _invoke(runner, base, "clear", "dev")
    assert result.exit_code == 0
    assert "Cleared" in result.output
    list_result = _invoke(runner, base, "list", "dev")
    assert "No changes" in list_result.output
