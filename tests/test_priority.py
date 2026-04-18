"""Tests for envoy_cli.priority."""
import pytest
from envoy_cli.priority import (
    PriorityError,
    set_priority,
    get_priority,
    remove_priority,
    list_priorities,
    _priority_path,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_priority(base):
    set_priority(base, "production", 10)
    assert get_priority(base, "production") == 10


def test_set_creates_file(base):
    set_priority(base, "staging", 5)
    assert _priority_path(base).exists()


def test_get_missing_raises(base):
    with pytest.raises(PriorityError, match="No priority set"):
        get_priority(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(PriorityError, match="must not be empty"):
        set_priority(base, "", 1)


def test_set_invalid_priority_type_raises(base):
    with pytest.raises(PriorityError, match="must be an integer"):
        set_priority(base, "prod", "high")  # type: ignore


def test_remove_priority(base):
    set_priority(base, "dev", 3)
    remove_priority(base, "dev")
    with pytest.raises(PriorityError):
        get_priority(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(PriorityError, match="No priority set"):
        remove_priority(base, "nonexistent")


def test_list_priorities_sorted_descending(base):
    set_priority(base, "dev", 1)
    set_priority(base, "production", 10)
    set_priority(base, "staging", 5)
    result = list_priorities(base)
    names = [name for name, _ in result]
    assert names == ["production", "staging", "dev"]


def test_list_priorities_empty(base):
    assert list_priorities(base) == []


def test_overwrite_priority(base):
    set_priority(base, "prod", 7)
    set_priority(base, "prod", 99)
    assert get_priority(base, "prod") == 99
