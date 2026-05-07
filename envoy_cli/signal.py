"""Signal module: attach named signals to env entries."""
from __future__ import annotations

import json
from pathlib import Path

VALID_SIGNALS = {"ok", "warn", "error", "unknown"}


class SignalError(Exception):
    pass


def _signals_path(base_dir: str) -> Path:
    return Path(base_dir) / "signals.json"


def _load(base_dir: str) -> dict:
    p = _signals_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _signals_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_signal(base_dir: str, env_name: str, level: str, message: str = "") -> None:
    """Attach a signal level (ok/warn/error/unknown) to an env entry."""
    if not env_name:
        raise SignalError("env_name must not be empty")
    if level not in VALID_SIGNALS:
        raise SignalError(f"Invalid signal level '{level}'. Choose from {sorted(VALID_SIGNALS)}")
    data = _load(base_dir)
    data[env_name] = {"level": level, "message": message}
    _save(base_dir, data)


def get_signal(base_dir: str, env_name: str) -> dict:
    """Return the signal dict for an env entry, defaulting to unknown."""
    if not env_name:
        raise SignalError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        return {"level": "unknown", "message": ""}
    return data[env_name]


def remove_signal(base_dir: str, env_name: str) -> None:
    """Remove the signal for an env entry."""
    if not env_name:
        raise SignalError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise SignalError(f"No signal found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_signals(base_dir: str) -> dict:
    """Return all recorded signals."""
    return _load(base_dir)
