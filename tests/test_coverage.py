"""Tests for envoy_cli.coverage."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.coverage import (
    CoverageError,
    CoverageReport,
    compute_coverage,
    get_coverage,
    list_coverage,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


CONTENT = """
# comment
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
DEBUG=true
"""

REQUIRED = ["DB_HOST", "DB_PORT", "SECRET_KEY", "API_KEY"]


def test_compute_coverage_basic(base: Path) -> None:
    report = compute_coverage("myenv", CONTENT, REQUIRED, base)
    assert report.env_name == "myenv"
    assert report.total_keys == 4
    assert set(report.present_keys) == {"DB_HOST", "DB_PORT", "SECRET_KEY"}
    assert report.missing_keys == ["API_KEY"]
    assert "DEBUG" in report.extra_keys
    assert report.score == pytest.approx(0.75)


def test_compute_coverage_perfect(base: Path) -> None:
    content = "DB_HOST=x\nDB_PORT=5432\n"
    report = compute_coverage("env2", content, ["DB_HOST", "DB_PORT"], base)
    assert report.score == pytest.approx(1.0)
    assert report.missing_keys == []


def test_compute_coverage_creates_file(base: Path) -> None:
    compute_coverage("env3", CONTENT, REQUIRED, base)
    assert (base / "coverage.json").exists()


def test_compute_coverage_empty_name_raises(base: Path) -> None:
    with pytest.raises(CoverageError, match="env_name"):
        compute_coverage("", CONTENT, REQUIRED, base)


def test_compute_coverage_empty_required_raises(base: Path) -> None:
    with pytest.raises(CoverageError, match="required_keys"):
        compute_coverage("env", CONTENT, [], base)


def test_get_coverage_returns_stored_report(base: Path) -> None:
    compute_coverage("env4", CONTENT, REQUIRED, base)
    report = get_coverage("env4", base)
    assert report.env_name == "env4"
    assert report.total_keys == 4
    assert report.score == pytest.approx(0.75)


def test_get_coverage_missing_raises(base: Path) -> None:
    with pytest.raises(CoverageError, match="No coverage report"):
        get_coverage("nonexistent", base)


def test_get_coverage_empty_name_raises(base: Path) -> None:
    with pytest.raises(CoverageError, match="env_name"):
        get_coverage("", base)


def test_list_coverage_empty(base: Path) -> None:
    assert list_coverage(base) == []


def test_list_coverage_returns_names(base: Path) -> None:
    compute_coverage("alpha", CONTENT, REQUIRED, base)
    compute_coverage("beta", CONTENT, ["DB_HOST"], base)
    names = list_coverage(base)
    assert set(names) == {"alpha", "beta"}


def test_summary_string(base: Path) -> None:
    report = compute_coverage("env5", CONTENT, REQUIRED, base)
    summary = report.summary
    assert "75%" in summary
    assert "env5" in summary
    assert "3/4" in summary


def test_compute_coverage_ignores_comments_and_blanks(base: Path) -> None:
    content = "# DB_HOST=x\n\nDB_HOST=real\n"
    report = compute_coverage("env6", content, ["DB_HOST"], base)
    assert report.present_keys == ["DB_HOST"]
    assert report.score == pytest.approx(1.0)
