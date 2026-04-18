"""Reminders: notify when an env var is stale or approaching TTL expiry."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envoy_cli.ttl import get_ttl, TTLError


class ReminderError(Exception):
    pass


def _reminders_path(base_dir: str) -> Path:
    return Path(base_dir) / "reminders.json"


def _load(base_dir: str) -> dict:
    p = _reminders_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _reminders_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_reminder(base_dir: str, env_name: str, message: str, remind_at: str) -> dict:
    """Register a reminder for env_name at remind_at (ISO-8601 string)."""
    if not env_name:
        raise ReminderError("env_name must not be empty")
    try:
        dt = datetime.fromisoformat(remind_at)
    except ValueError:
        raise ReminderError(f"Invalid datetime: {remind_at}")
    data = _load(base_dir)
    data[env_name] = {"message": message, "remind_at": dt.isoformat(), "dismissed": False}
    _save(base_dir, data)
    return data[env_name]


def get_reminder(base_dir: str, env_name: str) -> dict:
    data = _load(base_dir)
    if env_name not in data:
        raise ReminderError(f"No reminder found for '{env_name}'")
    return data[env_name]


def dismiss_reminder(base_dir: str, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise ReminderError(f"No reminder found for '{env_name}'")
    data[env_name]["dismissed"] = True
    _save(base_dir, data)


def due_reminders(base_dir: str) -> List[dict]:
    """Return all non-dismissed reminders whose remind_at <= now."""
    now = datetime.now(timezone.utc)
    data = _load(base_dir)
    results = []
    for env_name, info in data.items():
        if info.get("dismissed"):
            continue
        remind_at = datetime.fromisoformat(info["remind_at"])
        if remind_at.tzinfo is None:
            remind_at = remind_at.replace(tzinfo=timezone.utc)
        if remind_at <= now:
            results.append({"env_name": env_name, **info})
    return results


def list_reminders(base_dir: str) -> List[dict]:
    data = _load(base_dir)
    return [{"env_name": k, **v} for k, v in data.items()]
