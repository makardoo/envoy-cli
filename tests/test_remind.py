"""Tests for envoy_cli.remind."""
import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from envoy_cli.remind import (
    set_reminder, get_reminder, dismiss_reminder,
    due_reminders, list_reminders, ReminderError
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def _future(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _past(days=1):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def test_set_and_get_reminder(base):
    entry = set_reminder(base, "prod", "Rotate keys", _future())
    assert entry["message"] == "Rotate keys"
    assert entry["dismissed"] is False
    fetched = get_reminder(base, "prod")
    assert fetched["message"] == "Rotate keys"


def test_set_creates_file(base):
    set_reminder(base, "staging", "Check vars", _future())
    assert (Path(base) / "reminders.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(ReminderError, match="No reminder"):
        get_reminder(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(ReminderError):
        set_reminder(base, "", "msg", _future())


def test_set_invalid_datetime_raises(base):
    with pytest.raises(ReminderError, match="Invalid datetime"):
        set_reminder(base, "prod", "msg", "not-a-date")


def test_dismiss_reminder(base):
    set_reminder(base, "prod", "msg", _future())
    dismiss_reminder(base, "prod")
    entry = get_reminder(base, "prod")
    assert entry["dismissed"] is True


def test_dismiss_missing_raises(base):
    with pytest.raises(ReminderError):
        dismiss_reminder(base, "ghost")


def test_due_reminders_returns_past(base):
    set_reminder(base, "prod", "overdue", _past())
    set_reminder(base, "dev", "future", _future())
    due = due_reminders(base)
    names = [d["env_name"] for d in due]
    assert "prod" in names
    assert "dev" not in names


def test_due_reminders_excludes_dismissed(base):
    set_reminder(base, "prod", "overdue", _past())
    dismiss_reminder(base, "prod")
    assert due_reminders(base) == []


def test_list_reminders_all(base):
    set_reminder(base, "a", "msg a", _future())
    set_reminder(base, "b", "msg b", _past())
    items = list_reminders(base)
    assert len(items) == 2
    names = {i["env_name"] for i in items}
    assert names == {"a", "b"}
