"""Tests for envoy_cli.trigger."""
import pytest
from envoy_cli.trigger import (
    TriggerError,
    add_trigger,
    remove_trigger,
    get_triggers,
    list_triggers,
    clear_triggers,
    VALID_EVENTS,
    _triggers_path,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_add_and_get_trigger(base):
    add_trigger(base, "myenv", "on_set", "echo hello")
    cmds = get_triggers(base, "myenv", "on_set")
    assert "echo hello" in cmds


def test_add_creates_file(base):
    add_trigger(base, "myenv", "on_push", "deploy.sh")
    assert _triggers_path(base).exists()


def test_add_duplicate_not_duplicated(base):
    add_trigger(base, "myenv", "on_set", "echo hi")
    add_trigger(base, "myenv", "on_set", "echo hi")
    assert get_triggers(base, "myenv", "on_set").count("echo hi") == 1


def test_add_multiple_commands_for_event(base):
    add_trigger(base, "myenv", "on_get", "cmd_a")
    add_trigger(base, "myenv", "on_get", "cmd_b")
    cmds = get_triggers(base, "myenv", "on_get")
    assert "cmd_a" in cmds
    assert "cmd_b" in cmds


def test_add_empty_name_raises(base):
    with pytest.raises(TriggerError):
        add_trigger(base, "", "on_set", "echo hi")


def test_add_empty_command_raises(base):
    with pytest.raises(TriggerError):
        add_trigger(base, "myenv", "on_set", "")


def test_add_invalid_event_raises(base):
    with pytest.raises(TriggerError, match="Invalid event"):
        add_trigger(base, "myenv", "on_fly", "echo hi")


def test_remove_trigger(base):
    add_trigger(base, "myenv", "on_delete", "cleanup.sh")
    remove_trigger(base, "myenv", "on_delete", "cleanup.sh")
    assert get_triggers(base, "myenv", "on_delete") == []


def test_remove_missing_trigger_raises(base):
    with pytest.raises(TriggerError):
        remove_trigger(base, "myenv", "on_set", "nonexistent")


def test_list_triggers_returns_all_events(base):
    add_trigger(base, "myenv", "on_set", "a")
    add_trigger(base, "myenv", "on_pull", "b")
    result = list_triggers(base, "myenv")
    assert "on_set" in result
    assert "on_pull" in result


def test_list_triggers_empty_for_unknown_env(base):
    assert list_triggers(base, "ghost") == {}


def test_clear_triggers(base):
    add_trigger(base, "myenv", "on_rotate", "notify.sh")
    clear_triggers(base, "myenv", "on_rotate")
    assert get_triggers(base, "myenv", "on_rotate") == []


def test_clear_invalid_event_raises(base):
    with pytest.raises(TriggerError, match="Invalid event"):
        clear_triggers(base, "myenv", "on_bogus")


def test_get_triggers_invalid_event_raises(base):
    with pytest.raises(TriggerError, match="Invalid event"):
        get_triggers(base, "myenv", "on_bogus")


def test_all_valid_events_accepted(base):
    for event in VALID_EVENTS:
        add_trigger(base, "myenv", event, f"cmd_{event}")
        assert f"cmd_{event}" in get_triggers(base, "myenv", event)
