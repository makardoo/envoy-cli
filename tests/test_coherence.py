"""Tests for envoy_cli.coherence."""

from __future__ import annotations

import pytest

from envoy_cli.coherence import (
    CoherenceError,
    CoherenceReport,
    compute_coherence,
    get_coherence,
    list_coherence,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


CLEAN_CONTENT = """APP_HOST=localhost
APP_PORT=8080
APP_DEBUG=false
"""

MIXED_CONTENT = """APP_HOST=localhost
db_password=secret
Port=8080
"""


def test_compute_coherence_clean_returns_high_score(base):
    report = compute_coherence("myenv", CLEAN_CONTENT, base)
    assert report.score >= 0.8
    assert report.coherent is True
    assert report.total_keys == 3


def test_compute_coherence_mixed_case_penalises(base):
    report = compute_coherence("myenv", MIXED_CONTENT, base)
    assert report.score < 1.0
    assert any("UPPER_SNAKE_CASE" in i for i in report.issues)


def test_compute_coherence_creates_file(base):
    from pathlib import Path
    compute_coherence("myenv", CLEAN_CONTENT, base)
    assert (Path(base) / "coherence.json").exists()


def test_compute_coherence_empty_content_returns_zero(base):
    report = compute_coherence("myenv", "", base)
    assert report.score == 0.0
    assert report.total_keys == 0


def test_compute_coherence_ignores_comments_and_blanks(base):
    content = "# comment\n\nAPP_KEY=value\n"
    report = compute_coherence("myenv", content, base)
    assert report.total_keys == 1


def test_compute_coherence_empty_name_raises(base):
    with pytest.raises(CoherenceError):
        compute_coherence("", CLEAN_CONTENT, base)


def test_get_coherence_returns_stored_report(base):
    compute_coherence("prod", CLEAN_CONTENT, base)
    report = get_coherence("prod", base)
    assert report.env_name == "prod"
    assert report.score >= 0.8


def test_get_coherence_missing_raises(base):
    with pytest.raises(CoherenceError):
        get_coherence("nonexistent", base)


def test_get_coherence_empty_name_raises(base):
    with pytest.raises(CoherenceError):
        get_coherence("", base)


def test_list_coherence_empty(base):
    assert list_coherence(base) == []


def test_list_coherence_returns_all(base):
    compute_coherence("env1", CLEAN_CONTENT, base)
    compute_coherence("env2", MIXED_CONTENT, base)
    results = list_coherence(base)
    names = {r.env_name for r in results}
    assert names == {"env1", "env2"}


def test_coherence_report_summary_format(base):
    report = CoherenceReport(env_name="test", score=0.85, total_keys=5, issues=[])
    summary = report.summary()
    assert "test" in summary
    assert "0.85" in summary
    assert "coherent" in summary


def test_coherence_report_incoherent_label(base):
    report = CoherenceReport(env_name="test", score=0.5, total_keys=3, issues=["bad case"])
    assert "incoherent" in report.summary()
    assert report.coherent is False
