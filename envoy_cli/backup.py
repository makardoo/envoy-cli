"""Backup and restore named env backups (distinct from snapshots)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


class BackupError(Exception):
    pass


def _backup_dir(base_dir: str) -> Path:
    p = Path(base_dir) / ".envoy" / "backups"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _backup_path(base_dir: str, name: str, label: str) -> Path:
    safe_label = label.replace(" ", "_")
    return _backup_dir(base_dir) / f"{name}__{safe_label}.json"


def create_backup(base_dir: str, name: str, label: str, content: str) -> Path:
    if not name:
        raise BackupError("env name must not be empty")
    if not label:
        raise BackupError("label must not be empty")
    path = _backup_path(base_dir, name, label)
    if path.exists():
        raise BackupError(f"backup '{label}' already exists for env '{name}'")
    data = {
        "env": name,
        "label": label,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "content": content,
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def list_backups(base_dir: str, name: str) -> list[dict]:
    d = _backup_dir(base_dir)
    results = []
    for f in sorted(d.glob(f"{name}__*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append(data)
        except Exception:
            pass
    return results


def restore_backup(base_dir: str, name: str, label: str) -> str:
    path = _backup_path(base_dir, name, label)
    if not path.exists():
        raise BackupError(f"no backup '{label}' found for env '{name}'")
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["content"]


def delete_backup(base_dir: str, name: str, label: str) -> None:
    path = _backup_path(base_dir, name, label)
    if not path.exists():
        raise BackupError(f"no backup '{label}' found for env '{name}'")
    path.unlink()
