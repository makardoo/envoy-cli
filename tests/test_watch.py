"""Tests for envoy_cli.watch."""
from __future__ import annotations
import time
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from envoy_cli.watch import watch_file, build_sync_callback, WatchError


def test_watch_file_raises_if_not_found(tmp_path):
    with pytest.raises(WatchError, match="File not found"):
        watch_file(str(tmp_path / "missing.env"), on_change=lambda p: None, max_iterations=1)


def test_watch_file_calls_on_change_when_modified(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")

    called_with = []

    def _on_change(path):
        called_with.append(path)

    original_mtime = env_file.stat().st_mtime

    def _fake_sleep(_):
        # Simulate a file modification on first sleep
        if not called_with and not getattr(_fake_sleep, "modified", False):
            _fake_sleep.modified = True
            env_file.write_text("A=2")

    with patch("envoy_cli.watch.time.sleep", side_effect=_fake_sleep):
        watch_file(str(env_file), on_change=_on_change, interval=0.01, max_iterations=3)

    assert len(called_with) >= 1
    assert called_with[0] == str(env_file)


def test_watch_file_no_change_does_not_call_callback(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")

    called = []

    with patch("envoy_cli.watch.time.sleep"):
        watch_file(str(env_file), on_change=lambda p: called.append(p), interval=0.01, max_iterations=3)

    assert called == []


def test_watch_file_callback_exception_does_not_stop_watching(tmp_path):
    """Verify that an exception raised in on_change does not abort the watch loop."""
    env_file = tmp_path / ".env"
    env_file.write_text("A=1")

    call_count = [0]

    def _on_change(path):
        call_count[0] += 1
        raise RuntimeError("callback failure")

    def _fake_sleep(_):
        if not getattr(_fake_sleep, "modified", False):
            _fake_sleep.modified = True
            env_file.write_text("A=2")

    with patch("envoy_cli.watch.time.sleep", side_effect=_fake_sleep):
        # Should not propagate the RuntimeError from the callback
        watch_file(str(env_file), on_change=_on_change, interval=0.01, max_iterations=3)

    assert call_count[0] >= 1


def test_build_sync_callback_calls_push_env(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=val")

    with patch("envoy_cli.watch.push_env") as mock_push:
        cb = build_sync_callback(
            env_name="staging",
            passphrase="secret",
            remote_dir=str(tmp_path / "remote"),
            local_dir=str(tmp_path / "local"),
        )
        cb(str(env_file))

    mock_push.assert_called_once_with(
        "staging",
        "KEY=val",
        "secret",
        remote_dir=str(tmp_path / "remote"),
        local_dir=str(tmp_path / "local"),
    )
