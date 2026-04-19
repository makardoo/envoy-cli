"""Tests for envoy_cli.checksum module."""

import pytest
from pathlib import Path
from envoy_cli.checksum import (
    ChecksumError,
    compute_checksum,
    record_checksum,
    get_checksum,
    verify_checksum,
    remove_checksum,
    list_checksums,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_compute_checksum_returns_hex_string():
    result = compute_checksum("KEY=value")
    assert isinstance(result, str)
    assert len(result) == 64


def test_compute_checksum_is_deterministic():
    assert compute_checksum("KEY=value") == compute_checksum("KEY=value")


def test_compute_checksum_differs_for_different_content():
    assert compute_checksum("A=1") != compute_checksum("A=2")


def test_record_checksum_creates_file(base):
    record_checksum(base, "production", "KEY=value")
    assert (Path(base) / ".checksums.json").exists()


def test_record_checksum_returns_checksum(base):
    result = record_checksum(base, "staging", "KEY=value")
    assert result == compute_checksum("KEY=value")


def test_get_checksum_returns_stored_value(base):
    record_checksum(base, "dev", "X=1")
    assert get_checksum(base, "dev") == compute_checksum("X=1")


def test_get_checksum_raises_if_not_found(base):
    with pytest.raises(ChecksumError, match="No checksum recorded"):
        get_checksum(base, "missing")


def test_verify_checksum_returns_true_on_match(base):
    content = "KEY=secret\nOTHER=val"
    record_checksum(base, "prod", content)
    assert verify_checksum(base, "prod", content) is True


def test_verify_checksum_returns_false_on_mismatch(base):
    record_checksum(base, "prod", "KEY=original")
    assert verify_checksum(base, "prod", "KEY=tampered") is False


def test_verify_checksum_returns_false_if_not_recorded(base):
    assert verify_checksum(base, "nonexistent", "KEY=val") is False


def test_remove_checksum_deletes_entry(base):
    record_checksum(base, "dev", "A=1")
    remove_checksum(base, "dev")
    with pytest.raises(ChecksumError):
        get_checksum(base, "dev")


def test_remove_checksum_raises_if_not_found(base):
    with pytest.raises(ChecksumError, match="No checksum recorded"):
        remove_checksum(base, "ghost")


def test_list_checksums_empty(base):
    assert list_checksums(base) == {}


def test_list_checksums_returns_all(base):
    record_checksum(base, "a", "A=1")
    record_checksum(base, "b", "B=2")
    result = list_checksums(base)
    assert set(result.keys()) == {"a", "b"}


def test_record_empty_name_raises(base):
    with pytest.raises(ChecksumError, match="must not be empty"):
        record_checksum(base, "", "content")
