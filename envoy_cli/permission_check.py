"""Permission checking utilities for envoy-cli."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from envoy_cli.access import get_permission, AccessError


class PermissionDenied(Exception):
    """Raised when a user lacks required permission."""


def check_permission(
    base_dir: Path,
    env_name: str,
    user: str,
    required: str,
) -> None:
    """Raise PermissionDenied if *user* does not hold *required* on *env_name*.

    *required* must be one of ``'read'`` or ``'readwrite'``.
    If no ACL entry exists for the user the access is denied.
    """
    if required not in ("read", "readwrite"):
        raise ValueError(f"Unknown permission level: {required!r}")

    try:
        granted = get_permission(base_dir, env_name, user)
    except AccessError:
        raise PermissionDenied(
            f"User '{user}' has no access to env '{env_name}'."
        )

    if required == "readwrite" and granted == "read":
        raise PermissionDenied(
            f"User '{user}' has read-only access to env '{env_name}'; "
            "readwrite required."
        )


def has_permission(
    base_dir: Path,
    env_name: str,
    user: str,
    required: str,
) -> bool:
    """Return True if *user* holds at least *required* on *env_name*."""
    try:
        check_permission(base_dir, env_name, user, required)
        return True
    except (PermissionDenied, ValueError):
        return False


def assert_readwrite(base_dir: Path, env_name: str, user: str) -> None:
    """Convenience wrapper — asserts readwrite permission."""
    check_permission(base_dir, env_name, user, "readwrite")


def assert_read(base_dir: Path, env_name: str, user: str) -> None:
    """Convenience wrapper — asserts at least read permission."""
    check_permission(base_dir, env_name, user, "read")
