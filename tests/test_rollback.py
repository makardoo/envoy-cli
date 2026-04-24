"""Tests for envoy_cli.rollback."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy_cli.storage import save_env, load_env
from envoy_cli.snapshot import create_snapshot
from envoy_cli.rollback import (
    RollbackError,
    list_rollback_points,
    rollback_to_snapshot,
    rollback_to_latest,
    latest_snapshot_name,
)

PASSPHRASE = "test-pass"
ENV_CONTENT = "KEY=value\nFOO=bar\n"
ENV_NAME = "production"


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def _seed(base: Path, content: str = ENV_CONTENT) -> None:
    save_env(base, ENV_NAME, content, PASSPHRASE)


# --- list_rollback_points ---

def test_list_rollback_points_empty(base: Path) -> None:
    _seed(base)
    points = list_rollback_points(base, ENV_NAME)
    assert points == []


def test_list_rollback_points_returns_snapshots(base: Path) -> None:
    _seed(base)
    create_snapshot(base, ENV_NAME, "snap1", PASSPHRASE)
    create_snapshot(base, ENV_NAME, "snap2", PASSPHRASE)
    points = list_rollback_points(base, ENV_NAME)
    assert "snap1" in points
    assert "snap2" in points


def test_list_rollback_points_empty_name_raises(base: Path) -> None:
    with pytest.raises(RollbackError):
        list_rollback_points(base, "")


# --- rollback_to_snapshot ---

def test_rollback_to_snapshot_restores_content(base: Path) -> None:
    _seed(base)
    create_snapshot(base, ENV_NAME, "v1", PASSPHRASE)
    # Overwrite with new content
    save_env(base, ENV_NAME, "KEY=changed\n", PASSPHRASE)
    rollback_to_snapshot(base, ENV_NAME, "v1", PASSPHRASE)
    restored = load_env(base, ENV_NAME, PASSPHRASE)
    assert restored == ENV_CONTENT


def test_rollback_to_snapshot_missing_raises(base: Path) -> None:
    _seed(base)
    with pytest.raises(RollbackError, match="not found"):
        rollback_to_snapshot(base, ENV_NAME, "nonexistent", PASSPHRASE)


def test_rollback_to_snapshot_empty_name_raises(base: Path) -> None:
    with pytest.raises(RollbackError):
        rollback_to_snapshot(base, "", "snap", PASSPHRASE)


# --- rollback_to_latest ---

def test_rollback_to_latest_restores_most_recent(base: Path) -> None:
    _seed(base)
    create_snapshot(base, ENV_NAME, "v1", PASSPHRASE)
    save_env(base, ENV_NAME, "KEY=changed\n", PASSPHRASE)
    rollback_to_latest(base, ENV_NAME, PASSPHRASE)
    restored = load_env(base, ENV_NAME, PASSPHRASE)
    assert restored == ENV_CONTENT


def test_rollback_to_latest_no_snapshots_raises(base: Path) -> None:
    _seed(base)
    with pytest.raises(RollbackError, match="No snapshots"):
        rollback_to_latest(base, ENV_NAME, PASSPHRASE)


# --- latest_snapshot_name ---

def test_latest_snapshot_name_none_when_empty(base: Path) -> None:
    _seed(base)
    assert latest_snapshot_name(base, ENV_NAME) is None


def test_latest_snapshot_name_returns_last(base: Path) -> None:
    _seed(base)
    create_snapshot(base, ENV_NAME, "aaa", PASSPHRASE)
    create_snapshot(base, ENV_NAME, "zzz", PASSPHRASE)
    name = latest_snapshot_name(base, ENV_NAME)
    assert name == "zzz"
