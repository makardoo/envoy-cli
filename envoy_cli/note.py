"""Per-environment freeform notes."""
from __future__ import annotations

import json
from pathlib import Path


class NoteError(Exception):
    pass


def _notes_path(base_dir: str | Path) -> Path:
    return Path(base_dir) / "notes.json"


def _load(base_dir: str | Path) -> dict[str, str]:
    p = _notes_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str | Path, data: dict[str, str]) -> None:
    p = _notes_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_note(base_dir: str | Path, env_name: str, text: str) -> None:
    """Set or overwrite a note for *env_name*."""
    if not env_name:
        raise NoteError("env_name must not be empty")
    data = _load(base_dir)
    data[env_name] = text
    _save(base_dir, data)


def get_note(base_dir: str | Path, env_name: str) -> str:
    """Return the note for *env_name*, raising NoteError if absent."""
    data = _load(base_dir)
    if env_name not in data:
        raise NoteError(f"No note found for '{env_name}'")
    return data[env_name]


def remove_note(base_dir: str | Path, env_name: str) -> None:
    """Delete the note for *env_name*."""
    data = _load(base_dir)
    if env_name not in data:
        raise NoteError(f"No note found for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_notes(base_dir: str | Path) -> dict[str, str]:
    """Return all env_name -> note mappings."""
    return _load(base_dir)
