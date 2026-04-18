"""Tests for envoy_cli.note."""
import pytest
from pathlib import Path
from envoy_cli.note import (
    NoteError,
    set_note,
    get_note,
    remove_note,
    list_notes,
    _notes_path,
)


@pytest.fixture
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_set_and_get_note(base):
    set_note(base, "production", "Handle with care")
    assert get_note(base, "production") == "Handle with care"


def test_set_creates_notes_file(base):
    set_note(base, "staging", "WIP")
    assert _notes_path(base).exists()


def test_get_missing_raises(base):
    with pytest.raises(NoteError, match="No note found"):
        get_note(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(NoteError, match="env_name must not be empty"):
        set_note(base, "", "some note")


def test_overwrite_note(base):
    set_note(base, "dev", "first")
    set_note(base, "dev", "second")
    assert get_note(base, "dev") == "second"


def test_remove_note(base):
    set_note(base, "dev", "to be removed")
    remove_note(base, "dev")
    with pytest.raises(NoteError):
        get_note(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(NoteError, match="No note found"):
        remove_note(base, "ghost")


def test_list_notes_empty(base):
    assert list_notes(base) == {}


def test_list_notes_returns_all(base):
    set_note(base, "dev", "note1")
    set_note(base, "prod", "note2")
    result = list_notes(base)
    assert result == {"dev": "note1", "prod": "note2"}


def test_notes_persisted_across_calls(base):
    set_note(base, "staging", "persistent")
    # reload by calling list_notes which reads from disk
    notes = list_notes(base)
    assert notes["staging"] == "persistent"
