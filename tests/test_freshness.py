"""Tests for envoy_cli.freshness."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import pytest

from envoy_cli.freshness import (
    FreshnessError,
    get_freshness,
    is_stale,
    list_freshness,
    remove_freshness,
    touch,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_touch_returns_iso_timestamp(base):
    ts = touch(base, "prod")
    # Should parse without error
    dt = datetime.fromisoformat(ts)
    assert dt.tzinfo is not None


def test_touch_creates_file(base):
    from pathlib import Path

    touch(base, "staging")
    assert (Path(base) / "freshness.json").exists()


def test_get_freshness_returns_recorded_timestamp(base):
    ts = touch(base, "dev")
    assert get_freshness(base, "dev") == ts


def test_get_freshness_raises_if_not_found(base):
    with pytest.raises(FreshnessError, match="No freshness record"):
        get_freshness(base, "missing")


def test_touch_empty_name_raises(base):
    with pytest.raises(FreshnessError):
        touch(base, "")


def test_touch_updates_existing_record(base):
    ts1 = touch(base, "prod")
    time.sleep(0.01)
    ts2 = touch(base, "prod")
    assert ts2 != ts1
    assert get_freshness(base, "prod") == ts2


def test_is_stale_fresh_returns_false(base):
    touch(base, "prod")
    # Just touched — should not be stale with a generous window
    assert is_stale(base, "prod", max_age_seconds=3600) is False


def test_is_stale_old_returns_true(base):
    # Manually write a very old timestamp
    import json
    from pathlib import Path

    old_ts = "2000-01-01T00:00:00+00:00"
    path = Path(base) / "freshness.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump({"legacy": old_ts}, fh)
    assert is_stale(base, "legacy", max_age_seconds=60) is True


def test_is_stale_negative_max_age_raises(base):
    touch(base, "prod")
    with pytest.raises(FreshnessError):
        is_stale(base, "prod", max_age_seconds=-1)


def test_remove_freshness_deletes_record(base):
    touch(base, "prod")
    remove_freshness(base, "prod")
    with pytest.raises(FreshnessError):
        get_freshness(base, "prod")


def test_remove_freshness_raises_if_not_found(base):
    with pytest.raises(FreshnessError):
        remove_freshness(base, "ghost")


def test_list_freshness_empty(base):
    assert list_freshness(base) == {}


def test_list_freshness_returns_all(base):
    touch(base, "prod")
    touch(base, "staging")
    result = list_freshness(base)
    assert set(result.keys()) == {"prod", "staging"}
