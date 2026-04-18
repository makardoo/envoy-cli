"""Status module: summarize the state of a stored env (locked, tagged, pinned, TTL, etc.)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import datetime

from envoy_cli.storage import env_file_path


class StatusError(Exception):
    pass


@dataclass
class EnvStatus:
    name: str
    exists: bool
    locked: bool = False
    pinned: Optional[str] = None          # snapshot/version label
    tags: list[str] = field(default_factory=list)
    ttl_expires: Optional[str] = None     # ISO-8601 string or None
    ttl_expired: bool = False
    namespace: Optional[str] = None
    priority: Optional[int] = None
    archived: bool = False


def get_status(name: str, base_dir: str) -> EnvStatus:
    """Collect status information for *name* from all subsystems."""
    if not name:
        raise StatusError("env name must not be empty")

    exists = Path(env_file_path(name, base_dir)).exists()
    status = EnvStatus(name=name, exists=exists)

    # --- locked ---
    try:
        from envoy_cli.lock import is_locked
        status.locked = is_locked(name, base_dir)
    except Exception:
        pass

    # --- tags ---
    try:
        from envoy_cli.tag import get_tags
        status.tags = get_tags(name, base_dir)
    except Exception:
        pass

    # --- pin ---
    try:
        from envoy_cli.pin import get_pin
        pin = get_pin(name, base_dir)
        status.pinned = pin.get("label") or pin.get("snapshot")
    except Exception:
        pass

    # --- TTL ---
    try:
        from envoy_cli.ttl import get_ttl
        entry = get_ttl(name, base_dir)
        status.ttl_expires = entry.get("expires_at")
        if status.ttl_expires:
            exp = datetime.datetime.fromisoformat(status.ttl_expires)
            status.ttl_expired = datetime.datetime.utcnow() > exp
    except Exception:
        pass

    # --- namespace ---
    try:
        from envoy_cli.namespace import get_namespace
        status.namespace = get_namespace(name, base_dir)
    except Exception:
        pass

    # --- priority ---
    try:
        from envoy_cli.priority import get_priority
        status.priority = get_priority(name, base_dir)
    except Exception:
        pass

    # --- archived ---
    try:
        from envoy_cli.archive import is_archived
        status.archived = is_archived(name, base_dir)
    except Exception:
        pass

    return status
