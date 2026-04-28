"""Provenance tracking for env files.

Records the origin, creator, and chain-of-custody information
for each environment, enabling auditability of where an env
came from and how it was introduced into the system.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class ProvenanceError(Exception):
    """Raised for provenance-related errors."""


@dataclass
class ProvenanceRecord:
    """Represents the origin and custody chain of an env file."""

    env_name: str
    created_by: str
    created_at: str
    source: str  # e.g. 'manual', 'import', 'sync', 'clone'
    origin: Optional[str] = None  # e.g. file path, remote URL, parent env name
    notes: Optional[str] = None
    custody: List[dict] = field(default_factory=list)


def _provenance_path(base_dir: str) -> Path:
    return Path(base_dir) / "provenance.json"


def _load(base_dir: str) -> dict:
    path = _provenance_path(base_dir)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save(base_dir: str, data: dict) -> None:
    path = _provenance_path(base_dir)
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


VALID_SOURCES = {"manual", "import", "sync", "clone", "generated"}


def record_provenance(
    base_dir: str,
    env_name: str,
    created_by: str,
    source: str,
    origin: Optional[str] = None,
    notes: Optional[str] = None,
) -> ProvenanceRecord:
    """Record the provenance of an env file.

    Raises ProvenanceError if the env already has a provenance record,
    or if required fields are invalid.
    """
    if not env_name or not env_name.strip():
        raise ProvenanceError("env_name must not be empty")
    if not created_by or not created_by.strip():
        raise ProvenanceError("created_by must not be empty")
    if source not in VALID_SOURCES:
        raise ProvenanceError(
            f"Invalid source '{source}'. Must be one of: {sorted(VALID_SOURCES)}"
        )

    data = _load(base_dir)
    if env_name in data:
        raise ProvenanceError(
            f"Provenance already recorded for '{env_name}'. Use transfer_custody to update."
        )

    now = datetime.now(timezone.utc).isoformat()
    record = ProvenanceRecord(
        env_name=env_name,
        created_by=created_by,
        created_at=now,
        source=source,
        origin=origin,
        notes=notes,
        custody=[],
    )
    data[env_name] = asdict(record)
    _save(base_dir, data)
    return record


def get_provenance(base_dir: str, env_name: str) -> ProvenanceRecord:
    """Retrieve the provenance record for an env.

    Raises ProvenanceError if no record exists.
    """
    data = _load(base_dir)
    if env_name not in data:
        raise ProvenanceError(f"No provenance record found for '{env_name}'")
    raw = data[env_name]
    return ProvenanceRecord(**raw)


def transfer_custody(
    base_dir: str,
    env_name: str,
    transferred_by: str,
    reason: str,
) -> ProvenanceRecord:
    """Append a custody transfer entry to an existing provenance record.

    Raises ProvenanceError if no provenance record exists for the env.
    """
    if not transferred_by or not transferred_by.strip():
        raise ProvenanceError("transferred_by must not be empty")
    if not reason or not reason.strip():
        raise ProvenanceError("reason must not be empty")

    data = _load(base_dir)
    if env_name not in data:
        raise ProvenanceError(
            f"No provenance record found for '{env_name}'. Cannot transfer custody."
        )

    entry = {
        "transferred_by": transferred_by,
        "transferred_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    data[env_name]["custody"].append(entry)
    _save(base_dir, data)
    return ProvenanceRecord(**data[env_name])


def remove_provenance(base_dir: str, env_name: str) -> None:
    """Remove the provenance record for an env.

    Raises ProvenanceError if no record exists.
    """
    data = _load(base_dir)
    if env_name not in data:
        raise ProvenanceError(f"No provenance record found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_provenance(base_dir: str) -> List[ProvenanceRecord]:
    """Return all provenance records sorted by env name."""
    data = _load(base_dir)
    return [ProvenanceRecord(**v) for v in sorted(data.values(), key=lambda r: r["env_name"])]
