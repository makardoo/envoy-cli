"""Tests for envoy_cli.momentum."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.momentum import (
    MomentumError,
    clear_momentum,
    get_accesses,
    get_count,
    list_momentum,
    record_access,
)


@pytest.fixture
def base(tmp_path: Path) -> Path:
    return tmp_path / "store"


def test_record_access_returns_timestamp(base: Path) -> None:
    ts = record_access(base, "prod")
    assert isinstance(ts, str)
    assert "T" in ts  # ISO format


def test_record_access_creates_file(base: Path) -> None:
    record_access(base, "prod")
    assert (base / "momentum.json").exists()


def test_record_multiple_accesses(base: Path) -> None:
    record_access(base, "prod")
    record_access(base, "prod")
    record_access(base, "prod")
    assert get_count(base, "prod") == 3


def test_get_accesses_returns_list(base: Path) -> None:
    record_access(base, "staging")
    record_access(base, "staging")
    accesses = get_accesses(base, "staging")
    assert len(accesses) == 2
    for ts in accesses:
        assert isinstance(ts, str)


def test_get_accesses_missing_raises(base: Path) -> None:
    with pytest.raises(MomentumError, match="no momentum data"):
        get_accesses(base, "ghost")


def test_get_count_zero_for_single_access(base: Path) -> None:
    record_access(base, "dev")
    assert get_count(base, "dev") == 1


def test_clear_momentum_removes_entry(base: Path) -> None:
    record_access(base, "prod")
    clear_momentum(base, "prod")
    with pytest.raises(MomentumError):
        get_accesses(base, "prod")


def test_clear_momentum_missing_raises(base: Path) -> None:
    with pytest.raises(MomentumError, match="no momentum data"):
        clear_momentum(base, "ghost")


def test_list_momentum_empty(base: Path) -> None:
    assert list_momentum(base) == {}


def test_list_momentum_returns_counts(base: Path) -> None:
    record_access(base, "prod")
    record_access(base, "prod")
    record_access(base, "dev")
    result = list_momentum(base)
    assert result == {"prod": 2, "dev": 1}


def test_record_empty_name_raises(base: Path) -> None:
    with pytest.raises(MomentumError, match="must not be empty"):
        record_access(base, "")


def test_get_accesses_empty_name_raises(base: Path) -> None:
    with pytest.raises(MomentumError, match="must not be empty"):
        get_accesses(base, "  ")
