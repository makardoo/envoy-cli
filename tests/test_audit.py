"""Tests for envoy_cli.audit module."""

import json
import pytest
from pathlib import Path

from envoy_cli.audit import (
    append_audit_entry,
    read_audit_log,
    filter_audit_log,
    get_audit_log_path,
    AUDIT_FILENAME,
)


@pytest.fixture
def audit_dir(tmp_path):
    return str(tmp_path)


def test_get_audit_log_path_returns_correct_path(audit_dir):
    path = get_audit_log_path(audit_dir)
    assert path == Path(audit_dir) / AUDIT_FILENAME


def test_append_creates_log_file(audit_dir):
    append_audit_entry(audit_dir, "set", "myapp", "local")
    assert get_audit_log_path(audit_dir).exists()


def test_append_writes_valid_json_line(audit_dir):
    append_audit_entry(audit_dir, "set", "myapp", "local", user="alice")
    log_path = get_audit_log_path(audit_dir)
    lines = log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["action"] == "set"
    assert entry["env_name"] == "myapp"
    assert entry["environment"] == "local"
    assert entry["user"] == "alice"
    assert "timestamp" in entry


def test_append_multiple_entries(audit_dir):
    append_audit_entry(audit_dir, "set", "myapp", "local")
    append_audit_entry(audit_dir, "push", "myapp", "staging")
    append_audit_entry(audit_dir, "pull", "myapp", "production")
    entries = read_audit_log(audit_dir)
    assert len(entries) == 3


def test_read_audit_log_empty_if_no_file(audit_dir):
    entries = read_audit_log(audit_dir)
    assert entries == []


def test_filter_by_action(audit_dir):
    append_audit_entry(audit_dir, "set", "app1", "local")
    append_audit_entry(audit_dir, "push", "app1", "staging")
    append_audit_entry(audit_dir, "set", "app2", "local")
    entries = read_audit_log(audit_dir)
    result = filter_audit_log(entries, action="set")
    assert len(result) == 2
    assert all(e["action"] == "set" for e in result)


def test_filter_by_env_name(audit_dir):
    append_audit_entry(audit_dir, "set", "app1", "local")
    append_audit_entry(audit_dir, "set", "app2", "local")
    entries = read_audit_log(audit_dir)
    result = filter_audit_log(entries, env_name="app1")
    assert len(result) == 1
    assert result[0]["env_name"] == "app1"


def test_filter_by_environment(audit_dir):
    append_audit_entry(audit_dir, "push", "app1", "staging")
    append_audit_entry(audit_dir, "push", "app1", "production")
    entries = read_audit_log(audit_dir)
    result = filter_audit_log(entries, environment="staging")
    assert len(result) == 1
    assert result[0]["environment"] == "staging"


def test_append_includes_details(audit_dir):
    append_audit_entry(audit_dir, "remove", "app1", "local", details="forced removal")
    entries = read_audit_log(audit_dir)
    assert entries[0]["details"] == "forced removal"
