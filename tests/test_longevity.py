"""Tests for envoy_cli.longevity."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from envoy_cli.longevity import (
    LongevityError,
    delete_longevity,
    get_longevity,
    list_longevity,
    record_creation,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_record_creates_file(base: Path) -> None:
    record_creation(base, "prod")
    assert (base / "longevity.json").exists()


def test_record_returns_iso_timestamp(base: Path) -> None:
    ts = record_creation(base, "prod")
    # Should parse without error
    datetime.fromisoformat(ts)


def test_record_is_idempotent(base: Path) -> None:
    ts1 = record_creation(base, "prod")
    ts2 = record_creation(base, "prod")
    assert ts1 == ts2


def test_record_empty_name_raises(base: Path) -> None:
    with pytest.raises(LongevityError):
        record_creation(base, "")


def test_get_longevity_returns_info(base: Path) -> None:
    record_creation(base, "staging")
    info = get_longevity(base, "staging")
    assert info["name"] == "staging"
    assert "created_at" in info
    assert info["age_days"] >= 0


def test_get_longevity_missing_raises(base: Path) -> None:
    with pytest.raises(LongevityError, match="no longevity record"):
        get_longevity(base, "ghost")


def test_get_longevity_empty_name_raises(base: Path) -> None:
    with pytest.raises(LongevityError):
        get_longevity(base, "")


def test_age_days_old_entry(base: Path) -> None:
    """Manually plant an old timestamp and verify age_days reflects it."""
    old_dt = datetime.now(timezone.utc) - timedelta(days=30)
    data = {"legacy": {"created_at": old_dt.isoformat()}}
    p = base / "longevity.json"
    p.write_text(json.dumps(data))
    info = get_longevity(base, "legacy")
    assert info["age_days"] >= 30


def test_delete_longevity(base: Path) -> None:
    record_creation(base, "dev")
    delete_longevity(base, "dev")
    with pytest.raises(LongevityError):
        get_longevity(base, "dev")


def test_delete_missing_raises(base: Path) -> None:
    with pytest.raises(LongevityError):
        delete_longevity(base, "ghost")


def test_list_longevity_empty(base: Path) -> None:
    assert list_longevity(base) == []


def test_list_longevity_sorted_by_age_desc(base: Path) -> None:
    now = datetime.now(timezone.utc)
    data = {
        "new": {"created_at": (now - timedelta(days=1)).isoformat()},
        "old": {"created_at": (now - timedelta(days=100)).isoformat()},
        "mid": {"created_at": (now - timedelta(days=50)).isoformat()},
    }
    (base / "longevity.json").write_text(json.dumps(data))
    entries = list_longevity(base)
    names = [e["name"] for e in entries]
    assert names == ["old", "mid", "new"]
