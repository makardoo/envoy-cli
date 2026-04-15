"""Tests for envoy_cli.snapshot."""

from __future__ import annotations

import json
import time
import pytest

from envoy_cli.snapshot import (
    create_snapshot,
    list_snapshots,
    restore_snapshot,
    get_snapshot_dir,
    SnapshotError,
)
from envoy_cli.storage import save_env, load_env


@pytest.fixture()
def store(tmp_path):
    """Return a base_dir string pointing to a temp directory."""
    return str(tmp_path)


def _seed(store: str, name: str = "production", content: str = "KEY=value\n") -> None:
    save_env(name, content, base_dir=store)


# ---------------------------------------------------------------------------
# get_snapshot_dir
# ---------------------------------------------------------------------------

def test_snapshot_dir_is_created(store):
    snap_dir = get_snapshot_dir(base_dir=store)
    assert snap_dir.exists()
    assert snap_dir.is_dir()


# ---------------------------------------------------------------------------
# create_snapshot
# ---------------------------------------------------------------------------

def test_create_snapshot_returns_path(store):
    _seed(store)
    path = create_snapshot("production", base_dir=store)
    assert path.exists()


def test_create_snapshot_file_contains_valid_json(store):
    _seed(store, content="SECRET=abc\n")
    path = create_snapshot("production", base_dir=store)
    meta = json.loads(path.read_text())
    assert meta["env_name"] == "production"
    assert meta["content"] == "SECRET=abc\n"
    assert isinstance(meta["timestamp"], int)


def test_create_snapshot_raises_if_env_missing(store):
    with pytest.raises(SnapshotError, match="not found"):
        create_snapshot("nonexistent", base_dir=store)


# ---------------------------------------------------------------------------
# list_snapshots
# ---------------------------------------------------------------------------

def test_list_snapshots_empty_when_none_exist(store):
    assert list_snapshots("production", base_dir=store) == []


def test_list_snapshots_returns_all_snapshots(store):
    _seed(store)
    create_snapshot("production", base_dir=store)
    time.sleep(0.01)
    _seed(store, content="KEY=updated\n")
    create_snapshot("production", base_dir=store)
    snaps = list_snapshots("production", base_dir=store)
    assert len(snaps) == 2


def test_list_snapshots_only_returns_matching_env(store):
    _seed(store, name="staging")
    _seed(store, name="production")
    create_snapshot("staging", base_dir=store)
    snaps = list_snapshots("production", base_dir=store)
    assert snaps == []


# ---------------------------------------------------------------------------
# restore_snapshot
# ---------------------------------------------------------------------------

def test_restore_snapshot_recovers_content(store):
    _seed(store, content="ORIGINAL=1\n")
    path = create_snapshot("production", base_dir=store)
    meta = json.loads(path.read_text())
    ts = meta["timestamp"]

    # overwrite with new content
    save_env("production", "OVERWRITTEN=2\n", base_dir=store)

    restore_snapshot("production", ts, base_dir=store)
    assert load_env("production", base_dir=store) == "ORIGINAL=1\n"


def test_restore_snapshot_raises_if_snapshot_missing(store):
    _seed(store)
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot("production", 0, base_dir=store)
