"""Tests for envoy_cli.entropy."""
from __future__ import annotations

import math
from pathlib import Path

import pytest
from click.testing import CliRunner

from envoy_cli.entropy import (
    EntropyError,
    EntropyReport,
    shannon_entropy,
    compute_entropy,
)
from envoy_cli.cli_entropy import entropy_group
from envoy_cli.storage import save_env
from envoy_cli.crypto import encrypt


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


PASS = "hunter2"
CONTENT = "KEY1=short\nKEY2=aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789!@#\n"


def _seed(base: Path, content: str = CONTENT) -> None:
    encrypted = encrypt(content, PASS)
    save_env("myenv", encrypted, base_dir=base)


# ---------------------------------------------------------------------------
# Unit tests – shannon_entropy
# ---------------------------------------------------------------------------

def test_shannon_entropy_empty_string_is_zero():
    assert shannon_entropy("") == 0.0


def test_shannon_entropy_single_char_is_zero():
    assert shannon_entropy("aaaa") == 0.0


def test_shannon_entropy_two_equally_likely_chars():
    score = shannon_entropy("abababab")
    assert abs(score - 1.0) < 1e-9


def test_shannon_entropy_high_for_random_looking_string():
    score = shannon_entropy("aB3#xZ9!mQ2@pL5$")
    assert score > 3.0


# ---------------------------------------------------------------------------
# Unit tests – compute_entropy
# ---------------------------------------------------------------------------

def test_compute_entropy_returns_report(base: Path):
    _seed(base)
    report = compute_entropy("myenv", PASS, base_dir=base)
    assert isinstance(report, EntropyReport)
    assert report.env_name == "myenv"


def test_compute_entropy_scores_all_keys(base: Path):
    _seed(base)
    report = compute_entropy("myenv", PASS, base_dir=base)
    assert set(report.scores.keys()) == {"KEY1", "KEY2"}


def test_compute_entropy_high_entropy_key_flagged(base: Path):
    _seed(base)
    report = compute_entropy("myenv", PASS, base_dir=base)
    assert "KEY2" in report.high_entropy_keys


def test_compute_entropy_average_is_mean(base: Path):
    _seed(base)
    report = compute_entropy("myenv", PASS, base_dir=base)
    expected = sum(report.scores.values()) / len(report.scores)
    assert abs(report.average - round(expected, 4)) < 1e-6


def test_compute_entropy_raises_if_not_found(base: Path):
    with pytest.raises(EntropyError, match="not found"):
        compute_entropy("ghost", PASS, base_dir=base)


def test_compute_entropy_raises_on_wrong_passphrase(base: Path):
    _seed(base)
    with pytest.raises(EntropyError, match="Failed to decrypt"):
        compute_entropy("myenv", "wrongpass", base_dir=base)


def test_compute_entropy_empty_env_returns_zero_average(base: Path):
    encrypted = encrypt("", PASS)
    save_env("empty", encrypted, base_dir=base)
    report = compute_entropy("empty", PASS, base_dir=base)
    assert report.average == 0.0
    assert report.scores == {}


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_scan_exits_zero_for_low_entropy(runner, base: Path):
    content = "SIMPLE=abc\n"
    save_env("low", encrypt(content, PASS), base_dir=base)
    result = runner.invoke(
        entropy_group,
        ["scan", "low", "--passphrase", PASS, "--base-dir", str(base)],
    )
    assert result.exit_code == 0
    assert "SIMPLE" in result.output


def test_cli_scan_exits_two_for_high_entropy(runner, base: Path):
    _seed(base)
    result = runner.invoke(
        entropy_group,
        ["scan", "myenv", "--passphrase", PASS, "--base-dir", str(base)],
    )
    assert result.exit_code == 2
    assert "[HIGH]" in result.output


def test_cli_scan_exits_one_on_error(runner, base: Path):
    result = runner.invoke(
        entropy_group,
        ["scan", "missing", "--passphrase", PASS, "--base-dir", str(base)],
    )
    assert result.exit_code == 1


def test_cli_average_prints_number(runner, base: Path):
    _seed(base)
    result = runner.invoke(
        entropy_group,
        ["average", "myenv", "--passphrase", PASS, "--base-dir", str(base)],
    )
    assert result.exit_code == 0
    value = float(result.output.strip())
    assert value > 0.0
