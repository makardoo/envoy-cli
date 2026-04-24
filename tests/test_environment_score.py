"""Tests for envoy_cli.environment_score and envoy_cli.cli_score."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envoy_cli.environment_score import (
    ScoreError,
    compute_score,
    record_score,
    get_score,
    list_scores,
)
from envoy_cli.storage import save_env
from envoy_cli.env_file import encrypt_env
from envoy_cli import cli_score
from envoy_cli.cli_score import score_group

PASS = "hunter2"


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    cli_score._base_dir = tmp_path
    yield tmp_path
    cli_score._base_dir = None


def _seed(base: Path, env_name: str, content: str) -> None:
    encrypted = encrypt_env(content, PASS)
    save_env(env_name, encrypted, base_dir=base)


# --- compute_score ---

def test_compute_score_perfect(base: Path) -> None:
    _seed(base, "prod", "DB_HOST=localhost\nDB_PORT=5432\n")
    assert compute_score("prod", PASS, base_dir=base) == 100


def test_compute_score_penalises_empty_value(base: Path) -> None:
    _seed(base, "prod", "DB_HOST=\nDB_PORT=5432\n")
    score = compute_score("prod", PASS, base_dir=base)
    assert score < 100
    assert score >= 0


def test_compute_score_empty_env_returns_zero(base: Path) -> None:
    _seed(base, "empty", "# just a comment\n")
    assert compute_score("empty", PASS, base_dir=base) == 0


def test_compute_score_raises_if_env_missing(base: Path) -> None:
    with pytest.raises(ScoreError, match="not found"):
        compute_score("ghost", PASS, base_dir=base)


def test_compute_score_raises_empty_name(base: Path) -> None:
    with pytest.raises(ScoreError):
        compute_score("", PASS, base_dir=base)


# --- record / get / list ---

def test_record_and_get_score(base: Path) -> None:
    record_score("staging", 80, base_dir=base)
    rec = get_score("staging", base_dir=base)
    assert rec["env"] == "staging"
    assert rec["score"] == 80


def test_get_missing_raises(base: Path) -> None:
    with pytest.raises(ScoreError, match="no score recorded"):
        get_score("nope", base_dir=base)


def test_list_scores_sorted(base: Path) -> None:
    record_score("z_env", 60, base_dir=base)
    record_score("a_env", 90, base_dir=base)
    names = [r["env"] for r in list_scores(base_dir=base)]
    assert names == ["a_env", "z_env"]


def test_list_scores_empty(base: Path) -> None:
    assert list_scores(base_dir=base) == []


# --- CLI ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_compute_and_save(runner: CliRunner, base: Path) -> None:
    _seed(base, "prod", "API_KEY=abc\n")
    result = runner.invoke(score_group, ["compute", "prod", "-p", PASS, "--save"])
    assert result.exit_code == 0
    assert "/100" in result.output
    assert "saved" in result.output.lower()


def test_cli_compute_missing_exits_nonzero(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(score_group, ["compute", "ghost", "-p", PASS])
    assert result.exit_code != 0


def test_cli_show(runner: CliRunner, base: Path) -> None:
    record_score("dev", 60, base_dir=base)
    result = runner.invoke(score_group, ["show", "dev"])
    assert result.exit_code == 0
    assert "60/100" in result.output


def test_cli_show_missing_exits_nonzero(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(score_group, ["show", "nope"])
    assert result.exit_code != 0


def test_cli_list_empty(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(score_group, ["list"])
    assert result.exit_code == 0
    assert "No scores" in result.output


def test_cli_list_shows_entries(runner: CliRunner, base: Path) -> None:
    record_score("prod", 100, base_dir=base)
    result = runner.invoke(score_group, ["list"])
    assert "prod" in result.output
    assert "100/100" in result.output
