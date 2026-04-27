"""Tests for envoy_cli.reputation."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.reputation import (
    ReputationError,
    _SCORE_WEIGHTS,
    compute_reputation,
    list_reputations,
    record_event,
    reset_reputation,
    _score_to_level,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path / "envoy"


# ---------------------------------------------------------------------------
# record_event
# ---------------------------------------------------------------------------

def test_record_event_creates_file(base: Path) -> None:
    record_event(base, "prod", "snapshots")
    assert (base / "reputation.json").exists()


def test_record_event_increments_counter(base: Path) -> None:
    record_event(base, "prod", "snapshots")
    record_event(base, "prod", "snapshots")
    rep = compute_reputation(base, "prod")
    assert rep["counters"]["snapshots"] == 2  # type: ignore[index]


def test_record_event_unknown_raises(base: Path) -> None:
    with pytest.raises(ReputationError, match="Unknown reputation event"):
        record_event(base, "prod", "nonexistent_event")


def test_record_event_empty_name_raises(base: Path) -> None:
    with pytest.raises(ReputationError):
        record_event(base, "", "snapshots")


# ---------------------------------------------------------------------------
# compute_reputation
# ---------------------------------------------------------------------------

def test_compute_reputation_zero_score_for_new_env(base: Path) -> None:
    rep = compute_reputation(base, "staging")
    assert rep["score"] == 0
    assert rep["level"] == "untrusted"


def test_compute_reputation_score_increases(base: Path) -> None:
    for _ in range(5):
        record_event(base, "prod", "compliance_passes")  # weight=5 each
    rep = compute_reputation(base, "prod")
    assert rep["score"] == 25
    assert rep["level"] == "medium"


def test_compute_reputation_trusted_level(base: Path) -> None:
    for _ in range(10):
        record_event(base, "prod", "compliance_passes")  # 10*5=50
    for _ in range(10):
        record_event(base, "prod", "snapshots")           # 10*3=30  total=80
    rep = compute_reputation(base, "prod")
    assert rep["level"] == "trusted"


def test_compute_reputation_empty_name_raises(base: Path) -> None:
    with pytest.raises(ReputationError):
        compute_reputation(base, "")


# ---------------------------------------------------------------------------
# list_reputations
# ---------------------------------------------------------------------------

def test_list_reputations_empty(base: Path) -> None:
    assert list_reputations(base) == []


def test_list_reputations_returns_all(base: Path) -> None:
    record_event(base, "alpha", "audit_entries")
    record_event(base, "beta", "secret_scans_clean")
    reps = list_reputations(base)
    names = [r["env_name"] for r in reps]
    assert "alpha" in names
    assert "beta" in names


# ---------------------------------------------------------------------------
# reset_reputation
# ---------------------------------------------------------------------------

def test_reset_removes_record(base: Path) -> None:
    record_event(base, "prod", "snapshots")
    reset_reputation(base, "prod")
    rep = compute_reputation(base, "prod")
    assert rep["score"] == 0


def test_reset_missing_raises(base: Path) -> None:
    with pytest.raises(ReputationError, match="No reputation record"):
        reset_reputation(base, "ghost")


# ---------------------------------------------------------------------------
# _score_to_level
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score,expected", [
    (0, "untrusted"),
    (9, "untrusted"),
    (10, "low"),
    (24, "low"),
    (25, "medium"),
    (49, "medium"),
    (50, "high"),
    (79, "high"),
    (80, "trusted"),
    (200, "trusted"),
])
def test_score_to_level(score: int, expected: str) -> None:
    assert _score_to_level(score) == expected
