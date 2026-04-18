"""Track change history for env entries."""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


class HistoryError(Exception):
    pass


def _history_dir(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "history"


def _history_path(base_dir: str, env_name: str) -> Path:
    return _history_dir(base_dir) / f"{env_name}.jsonl"


def record_change(
    base_dir: str,
    env_name: str,
    action: str,
    actor: str = "local",
    note: str = "",
) -> Dict[str, Any]:
    """Append a history entry for env_name."""
    if not env_name:
        raise HistoryError("env_name must not be empty")
    _history_dir(base_dir).mkdir(parents=True, exist_ok=True)
    entry: Dict[str, Any] = {
        "env": env_name,
        "action": action,
        "actor": actor,
        "note": note,
        "ts": time.time(),
    }
    path = _history_path(base_dir, env_name)
    with path.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def get_history(
    base_dir: str,
    env_name: str,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return history entries for env_name, newest last."""
    path = _history_path(base_dir, env_name)
    if not path.exists():
        return []
    entries = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    if limit is not None:
        entries = entries[-limit:]
    return entries


def clear_history(base_dir: str, env_name: str) -> int:
    """Delete all history for env_name. Returns number of entries removed."""
    path = _history_path(base_dir, env_name)
    if not path.exists():
        return 0
    count = sum(1 for line in path.read_text().splitlines() if line.strip())
    path.unlink()
    return count
