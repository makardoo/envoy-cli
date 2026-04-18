"""Webhook notification support for envoy-cli."""
from __future__ import annotations
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class WebhookError(Exception):
    pass


@dataclass
class Webhook:
    url: str
    events: List[str] = field(default_factory=list)
    label: str = ""


def _webhooks_path(base_dir: str) -> Path:
    return Path(base_dir) / "webhooks.json"


def _load(base_dir: str) -> List[dict]:
    p = _webhooks_path(base_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save(base_dir: str, data: List[dict]) -> None:
    p = _webhooks_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def register_webhook(base_dir: str, url: str, events: List[str], label: str = "") -> Webhook:
    if not url:
        raise WebhookError("URL must not be empty.")
    data = _load(base_dir)
    for entry in data:
        if entry["url"] == url:
            raise WebhookError(f"Webhook already registered: {url}")
    wh = Webhook(url=url, events=events, label=label)
    data.append({"url": wh.url, "events": wh.events, "label": wh.label})
    _save(base_dir, data)
    return wh


def remove_webhook(base_dir: str, url: str) -> None:
    data = _load(base_dir)
    new_data = [e for e in data if e["url"] != url]
    if len(new_data) == len(data):
        raise WebhookError(f"Webhook not found: {url}")
    _save(base_dir, new_data)


def list_webhooks(base_dir: str) -> List[Webhook]:
    return [Webhook(**e) for e in _load(base_dir)]


def fire_webhook(url: str, payload: dict, timeout: int = 5) -> int:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.URLError as exc:
        raise WebhookError(f"Failed to fire webhook {url}: {exc}") from exc


def notify(base_dir: str, event: str, payload: dict) -> List[str]:
    """Fire all webhooks registered for *event*. Returns list of fired URLs."""
    fired: List[str] = []
    for wh in list_webhooks(base_dir):
        if not wh.events or event in wh.events:
            fire_webhook(wh.url, {"event": event, **payload})
            fired.append(wh.url)
    return fired
