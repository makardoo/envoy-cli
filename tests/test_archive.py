"""Tests for envoy_cli.archive."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.archive import (
    archive_env,
    restore_env,
    list_archived,
    delete_archived,
    ArchiveError,
    _archive_path,
)


@pytest.fixture()
def base(tmp_path: Path) -> str:
    return str(tmp_path)


def test_archive_creates_file(base: str) -> None:
    archive_env(base, "prod", "KEY=val")
    assert _archive_path(base).exists()


def test_archive_and_list(base: str) -> None:
    archive_env(base, "prod", "KEY=val")
    archive_env(base, "staging", "KEY=other")
    assert list_archived(base) == ["prod", "staging"]


def test_list_empty(base: str) -> None:
    assert list_archived(base) == []


def test_archive_duplicate_raises(base: str) -> None:
    archive_env(base, "prod", "KEY=val")
    with pytest.raises(ArchiveError, match="already archived"):
        archive_env(base, "prod", "KEY=other")


def test_archive_empty_name_raises(base: str) -> None:
    with pytest.raises(ArchiveError):
        archive_env(base, "", "KEY=val")


def test_restore_returns_content(base: str) -> None:
    archive_env(base, "prod", "KEY=val")
    content = restore_env(base, "prod")
    assert content == "KEY=val"


def test_restore_removes_from_archive(base: str) -> None:
    archive_env(base, "prod", "KEY=val")
    restore_env(base, "prod")
    assert "prod" not in list_archived(base)


def test_restore_missing_raises(base: str) -> None:
    with pytest.raises(ArchiveError, match="not found in archive"):
        restore_env(base, "ghost")


def test_delete_archived(base: str) -> None:
    archive_env(base, "prod", "KEY=val")
    delete_archived(base, "prod")
    assert list_archived(base) == []


def test_delete_missing_raises(base: str) -> None:
    with pytest.raises(ArchiveError, match="not found in archive"):
        delete_archived(base, "ghost")
