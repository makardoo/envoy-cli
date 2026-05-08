"""Tests for envoy_cli.velocity."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envoy_cli.velocity import (
    VelocityError,
    clear_changes,
    compute_velocity,
    get_changes,
    record_change,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_record_change_returns_timestamp(base: Path) -> None:
    ts = record_change(base, "staging")
    assert isinstance(ts, str)
    assert "T" in ts  # ISO format


def test_record_change_creates_file(base: Path) -> None:
    record_change(base, "staging")
    assert (base / "velocity.json").exists()


def test_record_multiple_changes(base: Path) -> None:
    record_change(base, "staging")
    record_change(base, "staging")
    record_change(base, "staging")
    assert len(get_changes(base, "staging")) == 3


def test_get_changes_empty_returns_empty_list(base: Path) -> None:
    assert get_changes(base, "missing") == []


def test_record_empty_name_raises(base: Path) -> None:
    with pytest.raises(VelocityError):
        record_change(base, "")


def test_get_changes_empty_name_raises(base: Path) -> None:
    with pytest.raises(VelocityError):
        get_changes(base, "")


def test_compute_velocity_total(base: Path) -> None:
    for _ in range(4):
        record_change(base, "prod")
    v = compute_velocity(base, "prod")
    assert v["total"] == 4
    assert v["env_name"] == "prod"


def test_compute_velocity_last_24h(base: Path) -> None:
    record_change(base, "prod")
    v = compute_velocity(base, "prod")
    assert v["last_24h"] == 1


def test_compute_velocity_no_changes(base: Path) -> None:
    v = compute_velocity(base, "empty")
    assert v["total"] == 0
    assert v["last_24h"] == 0
    assert v["last_change"] is None


def test_clear_changes_removes_entries(base: Path) -> None:
    record_change(base, "dev")
    record_change(base, "dev")
    clear_changes(base, "dev")
    assert get_changes(base, "dev") == []


def test_clear_changes_empty_name_raises(base: Path) -> None:
    with pytest.raises(VelocityError):
        clear_changes(base, "")


def test_changes_isolated_per_env(base: Path) -> None:
    record_change(base, "a")
    record_change(base, "a")
    record_change(base, "b")
    assert len(get_changes(base, "a")) == 2
    assert len(get_changes(base, "b")) == 1
