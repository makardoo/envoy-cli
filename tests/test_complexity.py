"""Tests for envoy_cli.complexity."""

import pytest

from envoy_cli.complexity import (
    ComplexityError,
    ComplexityReport,
    compute_complexity,
    get_complexity,
    list_complexity,
    record_complexity,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


SIMPLE_CONTENT = "KEY1=value1\nKEY2=value2\n"
COMPLEX_CONTENT = "\n".join(
    [f"KEY{i}={'x' * (i * 10)}" for i in range(1, 11)]
)


def test_compute_complexity_basic():
    report = compute_complexity("dev", SIMPLE_CONTENT)
    assert report.env_name == "dev"
    assert report.key_count == 2
    assert isinstance(report.score, int)
    assert report.level in ("low", "medium", "high")


def test_compute_complexity_empty_content():
    report = compute_complexity("dev", "")
    assert report.key_count == 0
    assert report.score == 0
    assert report.level == "low"


def test_compute_complexity_ignores_comments_and_blanks():
    content = "# comment\n\nKEY=value\n"
    report = compute_complexity("dev", content)
    assert report.key_count == 1


def test_compute_complexity_empty_name_raises():
    with pytest.raises(ComplexityError):
        compute_complexity("", SIMPLE_CONTENT)


def test_compute_complexity_long_values_increase_score():
    short_report = compute_complexity("dev", "KEY=short\n")
    long_report = compute_complexity("dev", "KEY=" + "x" * 100 + "\n")
    assert long_report.score >= short_report.score


def test_compute_complexity_level_low():
    report = compute_complexity("dev", "A=1\n")
    assert report.level == "low"


def test_record_and_get_complexity(base):
    report = compute_complexity("staging", SIMPLE_CONTENT)
    record_complexity(base, report)
    fetched = get_complexity(base, "staging")
    assert fetched.env_name == "staging"
    assert fetched.key_count == report.key_count
    assert fetched.score == report.score
    assert fetched.level == report.level


def test_record_creates_file(base):
    from pathlib import Path
    report = compute_complexity("prod", SIMPLE_CONTENT)
    record_complexity(base, report)
    assert (Path(base) / "complexity.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(ComplexityError, match="No complexity record"):
        get_complexity(base, "nonexistent")


def test_list_empty(base):
    assert list_complexity(base) == []


def test_list_shows_entries(base):
    for name in ("dev", "staging", "prod"):
        record_complexity(base, compute_complexity(name, SIMPLE_CONTENT))
    results = list_complexity(base)
    names = {r.env_name for r in results}
    assert names == {"dev", "staging", "prod"}


def test_record_overwrites_existing(base):
    r1 = compute_complexity("dev", "A=1\n")
    record_complexity(base, r1)
    r2 = compute_complexity("dev", COMPLEX_CONTENT)
    record_complexity(base, r2)
    fetched = get_complexity(base, "dev")
    assert fetched.key_count == r2.key_count
