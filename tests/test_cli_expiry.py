"""Tests for envoy_cli.cli_expiry."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envoy_cli.cli_expiry import expiry_group

DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"


@pytest.fixture
def runner(tmp_path):
    r = CliRunner()
    with patch("envoy_cli.cli_expiry.get_env_dir", return_value=str(tmp_path)):
        yield r, tmp_path


def _future_str(days: int = 5) -> str:
    dt = datetime.now(tz=timezone.utc) + timedelta(days=days)
    return dt.strftime(DATE_FMT)


def _past_str(days: int = 1) -> str:
    dt = datetime.now(tz=timezone.utc) - timedelta(days=days)
    return dt.strftime(DATE_FMT)


def test_set_expiry(runner):
    r, _ = runner
    result = r.invoke(expiry_group, ["set", "prod", _future_str()])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_set_invalid_date_exits_nonzero(runner):
    r, _ = runner
    result = r.invoke(expiry_group, ["set", "prod", "not-a-date"])
    assert result.exit_code != 0


def test_get_expiry(runner):
    r, base = runner
    from envoy_cli.expiry import set_expiry
    dt = datetime.now(tz=timezone.utc) + timedelta(days=3)
    set_expiry(base, "staging", dt)
    result = r.invoke(expiry_group, ["get", "staging"])
    assert result.exit_code == 0
    assert "staging" in result.output
    assert "active" in result.output


def test_get_expired_shows_expired(runner):
    r, base = runner
    from envoy_cli.expiry import set_expiry
    dt = datetime.now(tz=timezone.utc) - timedelta(days=2)
    set_expiry(base, "old", dt)
    result = r.invoke(expiry_group, ["get", "old"])
    assert result.exit_code == 0
    assert "EXPIRED" in result.output


def test_get_missing_exits_nonzero(runner):
    r, _ = runner
    result = r.invoke(expiry_group, ["get", "ghost"])
    assert result.exit_code != 0


def test_remove_expiry(runner):
    r, base = runner
    from envoy_cli.expiry import set_expiry
    set_expiry(base, "dev", datetime.now(tz=timezone.utc) + timedelta(days=1))
    result = r.invoke(expiry_group, ["remove", "dev"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_empty(runner):
    r, _ = runner
    result = r.invoke(expiry_group, ["list"])
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_list_shows_entries(runner):
    r, base = runner
    from envoy_cli.expiry import set_expiry
    set_expiry(base, "a", datetime.now(tz=timezone.utc) + timedelta(days=1))
    set_expiry(base, "b", datetime.now(tz=timezone.utc) - timedelta(days=1))
    result = r.invoke(expiry_group, ["list"])
    assert result.exit_code == 0
    assert "a" in result.output
    assert "b" in result.output
    assert "EXPIRED" in result.output
    assert "active" in result.output
