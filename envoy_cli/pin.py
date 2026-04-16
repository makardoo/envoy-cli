"""Pin a specific version/snapshot of an env for reproducible deployments."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class PinError(Exception):
    pass


def _pins_path(base_dir: str) -> Path:
    return Path(base_dir) / "pins.json"


def _load_pins(base_dir: str) -> dict:
    p = _pins_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(base_dir: str, data: dict) -> None:
    p = _pins_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def pin_env(base_dir: str, env_name: str, snapshot_id: str, label: Optional[str] = None) -> None:
    """Pin env_name to a specific snapshot_id with an optional label."""
    if not env_name:
        raise PinError("env_name must not be empty")
    if not snapshot_id:
        raise PinError("snapshot_id must not be empty")
    pins = _load_pins(base_dir)
    pins[env_name] = {"snapshot_id": snapshot_id, "label": label or ""}
    _save_pins(base_dir, pins)


def get_pin(base_dir: str, env_name: str) -> dict:
    """Return pin info for env_name or raise PinError."""
    pins = _load_pins(base_dir)
    if env_name not in pins:
        raise PinError(f"No pin found for env '{env_name}'")
    return pins[env_name]


def remove_pin(base_dir: str, env_name: str) -> None:
    """Remove pin for env_name."""
    pins = _load_pins(base_dir)
    if env_name not in pins:
        raise PinError(f"No pin found for env '{env_name}'")
    del pins[env_name]
    _save_pins(base_dir, pins)


def list_pins(base_dir: str) -> list[dict]:
    """Return list of all pinned envs."""
    pins = _load_pins(base_dir)
    return [
        {"env_name": k, "snapshot_id": v["snapshot_id"], "label": v["label"]}
        for k, v in pins.items()
    ]
