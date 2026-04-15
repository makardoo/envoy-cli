"""Audit log for tracking env file operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

AUDIT_FILENAME = "audit.log"


def get_audit_log_path(env_dir: str) -> Path:
    """Return the path to the audit log file."""
    return Path(env_dir) / AUDIT_FILENAME


def append_audit_entry(
    env_dir: str,
    action: str,
    env_name: str,
    environment: str,
    user: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    """Append a single audit log entry as a JSON line."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "env_name": env_name,
        "environment": environment,
        "user": user or os.environ.get("USER", "unknown"),
        "details": details,
    }
    log_path = get_audit_log_path(env_dir)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_audit_log(env_dir: str) -> List[dict]:
    """Read and parse all audit log entries."""
    log_path = get_audit_log_path(env_dir)
    if not log_path.exists():
        return []
    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def filter_audit_log(
    entries: List[dict],
    env_name: Optional[str] = None,
    action: Optional[str] = None,
    environment: Optional[str] = None,
) -> List[dict]:
    """Filter audit log entries by optional criteria."""
    result = entries
    if env_name:
        result = [e for e in result if e.get("env_name") == env_name]
    if action:
        result = [e for e in result if e.get("action") == action]
    if environment:
        result = [e for e in result if e.get("environment") == environment]
    return result
