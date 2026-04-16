import pytest
from pathlib import Path
from envoy_cli.hook import (
    register_hook, unregister_hook, list_hooks, run_hooks,
    HookError, HOOK_EVENTS
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_register_hook_creates_file(base):
    register_hook(base, "post-set", "echo hello")
    assert (Path(base) / "hooks.json").exists()


def test_register_and_list_hook(base):
    register_hook(base, "post-set", "echo hello")
    hooks = list_hooks(base)
    assert "post-set" in hooks
    assert "echo hello" in hooks["post-set"]


def test_register_duplicate_hook_not_duplicated(base):
    register_hook(base, "post-set", "echo hello")
    register_hook(base, "post-set", "echo hello")
    hooks = list_hooks(base)
    assert hooks["post-set"].count("echo hello") == 1


def test_register_multiple_commands_for_event(base):
    register_hook(base, "pre-push", "echo a")
    register_hook(base, "pre-push", "echo b")
    hooks = list_hooks(base, "pre-push")
    assert len(hooks["pre-push"]) == 2


def test_register_invalid_event_raises(base):
    with pytest.raises(HookError, match="Unknown event"):
        register_hook(base, "invalid-event", "echo x")


def test_unregister_hook(base):
    register_hook(base, "post-pull", "echo done")
    unregister_hook(base, "post-pull", "echo done")
    hooks = list_hooks(base)
    assert "post-pull" not in hooks


def test_unregister_missing_hook_raises(base):
    with pytest.raises(HookError):
        unregister_hook(base, "post-pull", "echo missing")


def test_list_hooks_empty(base):
    hooks = list_hooks(base)
    assert hooks == {}


def test_list_hooks_by_event(base):
    register_hook(base, "pre-get", "echo pre")
    register_hook(base, "post-get", "echo post")
    hooks = list_hooks(base, "pre-get")
    assert "pre-get" in hooks
    assert "post-get" not in hooks


def test_run_hooks_executes_command(base):
    register_hook(base, "post-set", "exit 0")
    run_hooks(base, "post-set")


def test_run_hooks_failing_command_raises(base):
    register_hook(base, "post-set", "exit 1")
    with pytest.raises(HookError, match="Hook command failed"):
        run_hooks(base, "post-set")


def test_run_hooks_no_hooks_registered(base):
    run_hooks(base, "pre-set")  # should not raise
