"""Tests for envoy_cli.sustainability."""

import pytest
from pathlib import Path
from envoy_cli.sustainability import (
    SustainabilityError,
    SustainabilityReport,
    compute_sustainability,
    get_sustainability,
    list_sustainability,
)


@pytest.fixture
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_compute_sustainability_perfect_score(base):
    report = compute_sustainability(
        base, "prod",
        has_comment=True, has_owner=True, has_ttl=True,
        has_schema=True, is_stable=True,
    )
    assert report.score == 100.0
    assert report.env_name == "prod"


def test_compute_sustainability_zero_score(base):
    report = compute_sustainability(base, "dev")
    assert report.score == 0.0


def test_compute_sustainability_partial_score(base):
    report = compute_sustainability(base, "staging", has_owner=True, has_comment=True)
    assert report.score == pytest.approx(45.0)


def test_compute_sustainability_creates_file(base):
    compute_sustainability(base, "prod", has_owner=True)
    assert (base / "sustainability.json").exists()


def test_compute_sustainability_empty_name_raises(base):
    with pytest.raises(SustainabilityError):
        compute_sustainability(base, "")


def test_get_sustainability_returns_report(base):
    compute_sustainability(base, "prod", has_schema=True)
    report = get_sustainability(base, "prod")
    assert isinstance(report, SustainabilityReport)
    assert report.has_schema is True
    assert report.env_name == "prod"


def test_get_sustainability_missing_raises(base):
    with pytest.raises(SustainabilityError):
        get_sustainability(base, "ghost")


def test_compute_sustainability_overwrites_previous(base):
    compute_sustainability(base, "prod")
    compute_sustainability(base, "prod", has_owner=True, is_stable=True)
    report = get_sustainability(base, "prod")
    assert report.has_owner is True
    assert report.is_stable is True
    assert report.score == pytest.approx(40.0)


def test_list_sustainability_empty(base):
    assert list_sustainability(base) == []


def test_list_sustainability_returns_all(base):
    compute_sustainability(base, "dev")
    compute_sustainability(base, "prod", has_owner=True)
    results = list_sustainability(base)
    names = {r.env_name for r in results}
    assert names == {"dev", "prod"}


def test_summary_grade_a(base):
    report = compute_sustainability(
        base, "prod",
        has_comment=True, has_owner=True, has_ttl=True,
        has_schema=True, is_stable=True,
    )
    assert "grade A" in report.summary()


def test_summary_grade_d(base):
    report = compute_sustainability(base, "dev")
    assert "grade D" in report.summary()
