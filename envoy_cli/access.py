"""Access control: per-env read/write permissions per profile."""
from __future__ import annotations
import json
from pathlib import Path


class AccessError(Exception):
    pass


def _access_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "access.json"


def _load_access(base_dir: str) -> dict:
    p = _access_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_access(base_dir: str, data: dict) -> None:
    p = _access_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_permission(base_dir: str, env_name: str, profile: str, can_read: bool, can_write: bool) -> None:
    if not env_name:
        raise AccessError("env_name must not be empty")
    if not profile:
        raise AccessError("profile must not be empty")
    data = _load_access(base_dir)
    data.setdefault(env_name, {})[profile] = {"read": can_read, "write": can_write}
    _save_access(base_dir, data)


def get_permission(base_dir: str, env_name: str, profile: str) -> dict:
    data = _load_access(base_dir)
    try:
        return data[env_name][profile]
    except KeyError:
        raise AccessError(f"No permission entry for env '{env_name}' profile '{profile}'")


def check_permission(base_dir: str, env_name: str, profile: str, action: str) -> bool:
    """Return True if allowed. action is 'read' or 'write'. Missing entry => allowed."""
    data = _load_access(base_dir)
    entry = data.get(env_name, {}).get(profile)
    if entry is None:
        return True
    return bool(entry.get(action, True))


def list_permissions(base_dir: str, env_name: str) -> dict:
    data = _load_access(base_dir)
    return data.get(env_name, {})


def remove_permission(base_dir: str, env_name: str, profile: str) -> None:
    data = _load_access(base_dir)
    if env_name not in data or profile not in data[env_name]:
        raise AccessError(f"No permission entry for env '{env_name}' profile '{profile}'")
    del data[env_name][profile]
    if not data[env_name]:
        del data[env_name]
    _save_access(base_dir, data)
