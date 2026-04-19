"""Event subscription and notification system for env changes."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict


class EventError(Exception):
    pass


def _events_path(base_dir: str) -> Path:
    return Path(base_dir) / "events" / "subscriptions.json"


def _load(base_dir: str) -> Dict[str, List[str]]:
    p = _events_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, List[str]]) -> None:
    p = _events_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


VALID_EVENTS = {"set", "get", "remove", "push", "pull", "rotate"}


def subscribe(base_dir: str, event: str, handler: str) -> None:
    """Subscribe a handler (command string) to an event."""
    if not event:
        raise EventError("Event name must not be empty.")
    if event not in VALID_EVENTS:
        raise EventError(f"Unknown event '{event}'. Valid: {sorted(VALID_EVENTS)}")
    if not handler:
        raise EventError("Handler must not be empty.")
    data = _load(base_dir)
    handlers = data.setdefault(event, [])
    if handler not in handlers:
        handlers.append(handler)
    _save(base_dir, data)


def unsubscribe(base_dir: str, event: str, handler: str) -> None:
    data = _load(base_dir)
    handlers = data.get(event, [])
    if handler not in handlers:
        raise EventError(f"Handler '{handler}' not subscribed to '{event}'.")
    handlers.remove(handler)
    data[event] = handlers
    _save(base_dir, data)


def get_subscribers(base_dir: str, event: str) -> List[str]:
    return _load(base_dir).get(event, [])


def list_all_subscriptions(base_dir: str) -> Dict[str, List[str]]:
    return _load(base_dir)
