"""Tests for envoy_cli.cadence."""
from __future__ import annotations

import json
import pytest

from envoy_cli.cadence import (
    CadenceError,
    get_cadence,
    list_cadences,
    remove_cadence,
    set_cadence,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_cadence(base):
    set_cadence(base, "production", "daily")
    assert get_cadence(base, "production") == "daily"


def test_set_creates_file(base):
    set_cadence(base, "staging", "weekly")
    import os
    assert os.path.exists(f"{base}/cadence.json")


def test_get_missing_returns_default(base):
    assert get_cadence(base, "nonexistent") == "manual"


def test_set_empty_name_raises(base):
    with pytest.raises(CadenceError):
        set_cadence(base, "", "daily")


def test_set_invalid_cadence_raises(base):
    with pytest.raises(CadenceError, match="Invalid cadence"):
        set_cadence(base, "dev", "quarterly")


def test_remove_cadence(base):
    set_cadence(base, "dev", "hourly")
    remove_cadence(base, "dev")
    assert get_cadence(base, "dev") == "manual"


def test_remove_missing_raises(base):
    with pytest.raises(CadenceError):
        remove_cadence(base, "ghost")


def test_list_cadences_empty(base):
    assert list_cadences(base) == {}


def test_list_cadences_returns_all(base):
    set_cadence(base, "prod", "daily")
    set_cadence(base, "dev", "manual")
    result = list_cadences(base)
    assert result == {"prod": "daily", "dev": "manual"}


def test_overwrite_cadence(base):
    set_cadence(base, "prod", "daily")
    set_cadence(base, "prod", "weekly")
    assert get_cadence(base, "prod") == "weekly"


def test_cadence_file_is_valid_json(base):
    set_cadence(base, "prod", "monthly")
    with open(f"{base}/cadence.json") as f:
        data = json.load(f)
    assert data["prod"] == "monthly"
