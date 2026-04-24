"""Tests for envoy_cli.cooldown."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envoy_cli.cooldown import (
    CooldownError,
    check_cooldown,
    get_cooldown,
    list_cooldowns,
    record_access,
    remove_cooldown,
    set_cooldown,
)


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path / "cooldowns"


def test_set_and_get_cooldown(base: Path) -> None:
    set_cooldown(base, "production", 120)
    assert get_cooldown(base, "production") == 120


def test_set_creates_file(base: Path) -> None:
    set_cooldown(base, "staging", 30)
    assert (base / "cooldowns.json").exists()


def test_get_missing_raises(base: Path) -> None:
    with pytest.raises(CooldownError, match="No cooldown"):
        get_cooldown(base, "ghost")


def test_set_empty_name_raises(base: Path) -> None:
    with pytest.raises(CooldownError):
        set_cooldown(base, "", 60)


def test_set_negative_seconds_raises(base: Path) -> None:
    with pytest.raises(CooldownError, match=">= 0"):
        set_cooldown(base, "dev", -1)


def test_set_zero_seconds_allowed(base: Path) -> None:
    set_cooldown(base, "dev", 0)
    assert get_cooldown(base, "dev") == 0


def test_remove_cooldown(base: Path) -> None:
    set_cooldown(base, "staging", 30)
    remove_cooldown(base, "staging")
    with pytest.raises(CooldownError):
        get_cooldown(base, "staging")


def test_remove_missing_raises(base: Path) -> None:
    with pytest.raises(CooldownError, match="No cooldown"):
        remove_cooldown(base, "nonexistent")


def test_record_access_returns_timestamp(base: Path) -> None:
    before = time.time()
    ts = record_access(base, "dev")
    after = time.time()
    assert before <= ts <= after


def test_record_access_empty_name_raises(base: Path) -> None:
    with pytest.raises(CooldownError):
        record_access(base, "")


def test_check_cooldown_no_access_passes(base: Path) -> None:
    set_cooldown(base, "dev", 60)
    # No access recorded yet — should not raise
    check_cooldown(base, "dev")


def test_check_cooldown_within_window_raises(base: Path) -> None:
    set_cooldown(base, "prod", 3600)
    record_access(base, "prod")
    with pytest.raises(CooldownError, match="cooldown"):
        check_cooldown(base, "prod")


def test_check_cooldown_after_window_passes(base: Path) -> None:
    set_cooldown(base, "ci", 0)
    record_access(base, "ci")
    # window is 0 seconds — should never be in cooldown
    check_cooldown(base, "ci")


def test_list_cooldowns_empty(base: Path) -> None:
    assert list_cooldowns(base) == []


def test_list_cooldowns_returns_entries(base: Path) -> None:
    set_cooldown(base, "alpha", 10)
    set_cooldown(base, "beta", 20)
    entries = list_cooldowns(base)
    names = {e["env"] for e in entries}
    assert names == {"alpha", "beta"}
    seconds = {e["env"]: e["seconds"] for e in entries}
    assert seconds["alpha"] == 10
    assert seconds["beta"] == 20
