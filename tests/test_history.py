"""Tests for envoy_cli.history."""
import time
import pytest
from pathlib import Path
from envoy_cli.history import record_change, get_history, clear_history, HistoryError


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_record_creates_file(base):
    record_change(base, "prod", "push")
    p = Path(base) / ".envoy" / "history" / "prod.jsonl"
    assert p.exists()


def test_record_returns_entry(base):
    entry = record_change(base, "prod", "push", actor="ci", note="deploy")
    assert entry["env"] == "prod"
    assert entry["action"] == "push"
    assert entry["actor"] == "ci"
    assert entry["note"] == "deploy"
    assert "ts" in entry


def test_get_history_empty(base):
    assert get_history(base, "staging") == []


def test_get_history_returns_entries(base):
    record_change(base, "prod", "push")
    record_change(base, "prod", "pull")
    entries = get_history(base, "prod")
    assert len(entries) == 2
    assert entries[0]["action"] == "push"
    assert entries[1]["action"] == "pull"


def test_get_history_limit(base):
    for i in range(5):
        record_change(base, "prod", f"action_{i}")
    entries = get_history(base, "prod", limit=3)
    assert len(entries) == 3
    assert entries[-1]["action"] == "action_4"


def test_clear_history_returns_count(base):
    record_change(base, "prod", "push")
    record_change(base, "prod", "pull")
    count = clear_history(base, "prod")
    assert count == 2


def test_clear_history_removes_file(base):
    record_change(base, "prod", "push")
    clear_history(base, "prod")
    assert get_history(base, "prod") == []


def test_clear_history_missing_returns_zero(base):
    assert clear_history(base, "nonexistent") == 0


def test_record_empty_name_raises(base):
    with pytest.raises(HistoryError):
        record_change(base, "", "push")


def test_multiple_envs_independent(base):
    record_change(base, "prod", "push")
    record_change(base, "staging", "pull")
    assert len(get_history(base, "prod")) == 1
    assert len(get_history(base, "staging")) == 1
