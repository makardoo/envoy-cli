"""Tests for envoy_cli.alignment."""
import pytest
from envoy_cli.alignment import (
    AlignmentError,
    AlignmentReport,
    compute_alignment,
    get_alignment,
    list_alignments,
)


REF = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=changeme\n"
FULL = "DB_HOST=prod.example.com\nDB_PORT=5432\nSECRET_KEY=abc123\n"
PARTIAL = "DB_HOST=prod.example.com\nDB_PORT=5432\n"
EXTRA = FULL + "EXTRA_KEY=oops\n"


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_compute_alignment_perfect(base):
    report = compute_alignment(base, "prod", FULL, REF)
    assert report.score == 100.0
    assert report.is_aligned
    assert report.missing == []
    assert report.extra == []
    assert sorted(report.matched) == ["DB_HOST", "DB_PORT", "SECRET_KEY"]


def test_compute_alignment_missing_key(base):
    report = compute_alignment(base, "staging", PARTIAL, REF)
    assert report.score < 100.0
    assert not report.is_aligned
    assert "SECRET_KEY" in report.missing
    assert report.extra == []


def test_compute_alignment_extra_key(base):
    report = compute_alignment(base, "dev", EXTRA, REF)
    assert report.score == 100.0  # all ref keys present
    assert "EXTRA_KEY" in report.extra


def test_compute_alignment_creates_file(base, tmp_path):
    compute_alignment(base, "prod", FULL, REF)
    assert (tmp_path / "alignment.json").exists()


def test_compute_alignment_empty_ref(base):
    report = compute_alignment(base, "prod", FULL, "")
    assert report.score == 0.0
    assert report.matched == []


def test_compute_alignment_empty_name_raises(base):
    with pytest.raises(AlignmentError):
        compute_alignment(base, "", FULL, REF)


def test_get_alignment_returns_report(base):
    compute_alignment(base, "prod", FULL, REF)
    report = get_alignment(base, "prod")
    assert isinstance(report, AlignmentReport)
    assert report.env_name == "prod"
    assert report.score == 100.0


def test_get_alignment_missing_raises(base):
    with pytest.raises(AlignmentError):
        get_alignment(base, "nonexistent")


def test_list_alignments_empty(base):
    assert list_alignments(base) == []


def test_list_alignments_returns_names(base):
    compute_alignment(base, "prod", FULL, REF)
    compute_alignment(base, "staging", PARTIAL, REF)
    names = list_alignments(base)
    assert "prod" in names
    assert "staging" in names


def test_compute_alignment_ignores_comments_and_blanks(base):
    content = "# comment\n\nDB_HOST=x\nDB_PORT=5432\nSECRET_KEY=y\n"
    report = compute_alignment(base, "prod", content, REF)
    assert report.score == 100.0


def test_report_to_dict_roundtrip(base):
    report = compute_alignment(base, "prod", FULL, REF)
    d = report.to_dict()
    assert d["env_name"] == "prod"
    assert d["score"] == 100.0
    assert isinstance(d["matched"], list)
