"""Scheduled sync jobs — store and manage sync schedules for environments."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional


class ScheduleError(Exception):
    pass


@dataclass
class SyncSchedule:
    env_name: str
    cron: str
    direction: str  # 'push' or 'pull'
    profile: str = "default"
    enabled: bool = True


def _schedules_path(base_dir: str) -> Path:
    return Path(base_dir) / "schedules.json"


def _load_schedules(base_dir: str) -> List[dict]:
    p = _schedules_path(base_dir)
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)


def _save_schedules(base_dir: str, schedules: List[dict]) -> None:
    p = _schedules_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(schedules, f, indent=2)


def add_schedule(base_dir: str, schedule: SyncSchedule) -> None:
    schedules = _load_schedules(base_dir)
    for s in schedules:
        if s["env_name"] == schedule.env_name and s["direction"] == schedule.direction:
            raise ScheduleError(
                f"Schedule for '{schedule.env_name}' ({schedule.direction}) already exists."
            )
    schedules.append(asdict(schedule))
    _save_schedules(base_dir, schedules)


def remove_schedule(base_dir: str, env_name: str, direction: str) -> None:
    schedules = _load_schedules(base_dir)
    new = [s for s in schedules if not (s["env_name"] == env_name and s["direction"] == direction)]
    if len(new) == len(schedules):
        raise ScheduleError(f"No schedule found for '{env_name}' ({direction}).")
    _save_schedules(base_dir, new)


def list_schedules(base_dir: str) -> List[SyncSchedule]:
    return [SyncSchedule(**s) for s in _load_schedules(base_dir)]


def get_schedule(base_dir: str, env_name: str, direction: str) -> SyncSchedule:
    for s in _load_schedules(base_dir):
        if s["env_name"] == env_name and s["direction"] == direction:
            return SyncSchedule(**s)
    raise ScheduleError(f"No schedule found for '{env_name}' ({direction}).")


def toggle_schedule(base_dir: str, env_name: str, direction: str, enabled: bool) -> None:
    schedules = _load_schedules(base_dir)
    found = False
    for s in schedules:
        if s["env_name"] == env_name and s["direction"] == direction:
            s["enabled"] = enabled
            found = True
    if not found:
        raise ScheduleError(f"No schedule found for '{env_name}' ({direction}).")
    _save_schedules(base_dir, schedules)
