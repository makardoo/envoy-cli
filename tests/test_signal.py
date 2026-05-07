"""Tests for envoy_cli.signal."""
from __future__ import annotations

import pytest

from envoy_cli.signal import (
    SignalError,
    set_signal,
    get_signal,
    remove_signal,
    list_signals,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_signal(base):
    set_signal(base, "myenv", "ok", "all good")
    info = get_signal(base, "myenv")
    assert info["level"] == "ok"
    assert info["message"] == "all good"


def test_set_creates_file(base):
    from pathlib import Path
    set_signal(base, "myenv", "warn")
    assert (Path(base) / "signals.json").exists()


def test_get_missing_returns_unknown(base):
    info = get_signal(base, "ghost")
    assert info["level"] == "unknown"
    assert info["message"] == ""


def test_set_empty_name_raises(base):
    with pytest.raises(SignalError):
        set_signal(base, "", "ok")


def test_get_empty_name_raises(base):
    with pytest.raises(SignalError):
        get_signal(base, "")


def test_set_invalid_level_raises(base):
    with pytest.raises(SignalError, match="Invalid signal level"):
        set_signal(base, "myenv", "critical")


def test_remove_signal(base):
    set_signal(base, "myenv", "error", "broken")
    remove_signal(base, "myenv")
    info = get_signal(base, "myenv")
    assert info["level"] == "unknown"


def test_remove_missing_raises(base):
    with pytest.raises(SignalError):
        remove_signal(base, "ghost")


def test_list_signals_empty(base):
    assert list_signals(base) == {}


def test_list_signals_returns_all(base):
    set_signal(base, "a", "ok")
    set_signal(base, "b", "warn", "check this")
    data = list_signals(base)
    assert "a" in data
    assert "b" in data
    assert data["b"]["message"] == "check this"


def test_overwrite_signal(base):
    set_signal(base, "myenv", "ok")
    set_signal(base, "myenv", "error", "now broken")
    info = get_signal(base, "myenv")
    assert info["level"] == "error"
    assert info["message"] == "now broken"
