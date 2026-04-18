"""Tests for envoy_cli.status."""
import pytest
from pathlib import Path

from envoy_cli.storage import save_env
from envoy_cli.status import get_status, StatusError


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def _seed(base: str, name: str = "prod") -> None:
    save_env(name, "KEY=val\n", "secret", base)


# ---------------------------------------------------------------------------
# basic
# ---------------------------------------------------------------------------

def test_get_status_exists(base):
    _seed(base)
    s = get_status("prod", base)
    assert s.exists is True
    assert s.name == "prod"


def test_get_status_not_exists(base):
    s = get_status("ghost", base)
    assert s.exists is False


def test_get_status_empty_name_raises(base):
    with pytest.raises(StatusError):
        get_status("", base)


# ---------------------------------------------------------------------------
# locked
# ---------------------------------------------------------------------------

def test_get_status_locked(base):
    _seed(base)
    from envoy_cli.lock import lock_env
    lock_env("prod", "secret", base)
    s = get_status("prod", base)
    assert s.locked is True


def test_get_status_not_locked(base):
    _seed(base)
    s = get_status("prod", base)
    assert s.locked is False


# ---------------------------------------------------------------------------
# tags
# ---------------------------------------------------------------------------

def test_get_status_tags(base):
    _seed(base)
    from envoy_cli.tag import add_tag
    add_tag("prod", "v1", base)
    add_tag("prod", "stable", base)
    s = get_status("prod", base)
    assert "v1" in s.tags
    assert "stable" in s.tags


def test_get_status_no_tags(base):
    _seed(base)
    s = get_status("prod", base)
    assert s.tags == []


# ---------------------------------------------------------------------------
# namespace
# ---------------------------------------------------------------------------

def test_get_status_namespace(base):
    _seed(base)
    from envoy_cli.namespace import assign_namespace
    assign_namespace("prod", "backend", base)
    s = get_status("prod", base)
    assert s.namespace == "backend"


# ---------------------------------------------------------------------------
# archived
# ---------------------------------------------------------------------------

def test_get_status_archived(base):
    _seed(base)
    from envoy_cli.archive import archive_env
    archive_env("prod", base)
    s = get_status("prod", base)
    assert s.archived is True
