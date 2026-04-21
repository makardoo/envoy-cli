"""Trigger module: associate shell commands with env lifecycle events."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

VALID_EVENTS = {"on_set", "on_get", "on_delete", "on_push", "on_pull", "on_rotate"}


class TriggerError(Exception):
    pass


def _triggers_path(base_dir: str) -> Path:
    return Path(base_dir) / "triggers.json"


def _load(base_dir: str) -> Dict[str, Dict[str, List[str]]]:
    p = _triggers_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, Dict[str, List[str]]]) -> None:
    p = _triggers_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_trigger(base_dir: str, env_name: str, event: str, command: str) -> None:
    """Register *command* to run when *event* fires for *env_name*."""
    if not env_name:
        raise TriggerError("env_name must not be empty")
    if event not in VALID_EVENTS:
        raise TriggerError(f"Invalid event '{event}'. Valid: {sorted(VALID_EVENTS)}")
    if not command:
        raise TriggerError("command must not be empty")
    data = _load(base_dir)
    env_triggers = data.setdefault(env_name, {})
    cmds = env_triggers.setdefault(event, [])
    if command not in cmds:
        cmds.append(command)
    _save(base_dir, data)


def remove_trigger(base_dir: str, env_name: str, event: str, command: str) -> None:
    """Unregister *command* from *event* for *env_name*."""
    data = _load(base_dir)
    try:
        data[env_name][event].remove(command)
    except (KeyError, ValueError):
        raise TriggerError(f"Trigger not found: {env_name}/{event}/{command}")
    _save(base_dir, data)


def get_triggers(base_dir: str, env_name: str, event: str) -> List[str]:
    """Return all commands registered for *event* on *env_name*."""
    if event not in VALID_EVENTS:
        raise TriggerError(f"Invalid event '{event}'")
    data = _load(base_dir)
    return list(data.get(env_name, {}).get(event, []))


def list_triggers(base_dir: str, env_name: str) -> Dict[str, List[str]]:
    """Return all triggers for *env_name* keyed by event."""
    data = _load(base_dir)
    return dict(data.get(env_name, {}))


def clear_triggers(base_dir: str, env_name: str, event: str) -> None:
    """Remove all commands for *event* on *env_name*."""
    if event not in VALID_EVENTS:
        raise TriggerError(f"Invalid event '{event}'")
    data = _load(base_dir)
    if env_name in data and event in data[env_name]:
        del data[env_name][event]
        _save(base_dir, data)
