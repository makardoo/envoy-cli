"""Tests for envoy_cli.lifecycle."""
import pytest
from pathlib import Path

from envoy_cli.lifecycle import (
    LifecycleError,
    get_state,
    list_states,
    remove_state,
    set_state,
)


@pytest.fixture
def base(tmp_path: Path) -> Path:
    return tmp_path


def test_set_and_get_state(base):
    set_state(base, "myenv", "draft")
    assert get_state(base, "myenv") == "draft"


def test_set_creates_file(base):
    set_state(base, "myenv", "draft")
    assert (base / ".envoy" / "lifecycle.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(LifecycleError, match="No lifecycle state"):
        get_state(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(LifecycleError, match="must not be empty"):
        set_state(base, "", "draft")


def test_set_invalid_state_raises(base):
    with pytest.raises(LifecycleError, match="Invalid state"):
        set_state(base, "myenv", "unknown")


def test_valid_transition(base):
    set_state(base, "myenv", "draft")
    set_state(base, "myenv", "active")
    assert get_state(base, "myenv") == "active"


def test_invalid_transition_raises(base):
    set_state(base, "myenv", "draft")
    with pytest.raises(LifecycleError, match="Cannot transition"):
        set_state(base, "myenv", "retired")


def test_transition_from_active_to_deprecated(base):
    set_state(base, "myenv", "draft")
    set_state(base, "myenv", "active")
    set_state(base, "myenv", "deprecated")
    assert get_state(base, "myenv") == "deprecated"


def test_retired_has_no_transitions(base):
    set_state(base, "myenv", "draft")
    set_state(base, "myenv", "active")
    set_state(base, "myenv", "deprecated")
    set_state(base, "myenv", "retired")
    with pytest.raises(LifecycleError, match="Cannot transition"):
        set_state(base, "myenv", "active")


def test_remove_state(base):
    set_state(base, "myenv", "draft")
    remove_state(base, "myenv")
    with pytest.raises(LifecycleError):
        get_state(base, "myenv")


def test_remove_missing_raises(base):
    with pytest.raises(LifecycleError, match="No lifecycle state"):
        remove_state(base, "ghost")


def test_list_states_empty(base):
    assert list_states(base) == {}


def test_list_states_returns_all(base):
    set_state(base, "a", "draft")
    set_state(base, "b", "draft")
    set_state(base, "b", "active")
    result = list_states(base)
    assert result == {"a": "draft", "b": "active"}
