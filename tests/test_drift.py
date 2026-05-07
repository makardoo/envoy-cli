"""Tests for envoy_cli.drift."""
import pytest

from envoy_cli.drift import detect_drift, DriftError, DriftReport
from envoy_cli.env_file import encrypt_env
from envoy_cli.storage import save_env


PASSPHRASE = "test-pass"


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def _seed(store: str, env_name: str, content: str) -> None:
    encrypted = encrypt_env(content, PASSPHRASE)
    save_env(env_name, encrypted, base_dir=store)


def test_no_drift_when_content_matches(store):
    content = "KEY1=val1\nKEY2=val2\n"
    _seed(store, "prod", content)
    report = detect_drift("prod", content, PASSPHRASE, base_dir=store)
    assert not report.has_drift
    assert report.added == []
    assert report.removed == []
    assert report.changed == []


def test_detects_added_key(store):
    stored = "KEY1=val1\n"
    live = "KEY1=val1\nKEY2=val2\n"
    _seed(store, "prod", stored)
    report = detect_drift("prod", live, PASSPHRASE, base_dir=store)
    assert report.has_drift
    assert "KEY2" in report.added
    assert report.removed == []
    assert report.changed == []


def test_detects_removed_key(store):
    stored = "KEY1=val1\nKEY2=val2\n"
    live = "KEY1=val1\n"
    _seed(store, "prod", stored)
    report = detect_drift("prod", live, PASSPHRASE, base_dir=store)
    assert report.has_drift
    assert "KEY2" in report.removed
    assert report.added == []


def test_detects_changed_value(store):
    stored = "KEY1=old\n"
    live = "KEY1=new\n"
    _seed(store, "prod", stored)
    report = detect_drift("prod", live, PASSPHRASE, base_dir=store)
    assert report.has_drift
    assert "KEY1" in report.changed


def test_ignores_comments_and_blanks(store):
    stored = "KEY1=val1\n"
    live = "# comment\n\nKEY1=val1\n"
    _seed(store, "prod", stored)
    report = detect_drift("prod", live, PASSPHRASE, base_dir=store)
    assert not report.has_drift


def test_raises_if_env_not_found(store):
    with pytest.raises(DriftError, match="No stored env"):
        detect_drift("missing", "KEY=val", PASSPHRASE, base_dir=store)


def test_raises_on_empty_env_name(store):
    with pytest.raises(DriftError):
        detect_drift("", "KEY=val", PASSPHRASE, base_dir=store)


def test_summary_no_drift(store):
    content = "A=1\n"
    _seed(store, "dev", content)
    report = detect_drift("dev", content, PASSPHRASE, base_dir=store)
    assert "no drift" in report.summary()


def test_summary_with_drift(store):
    _seed(store, "dev", "A=1\n")
    report = detect_drift("dev", "A=1\nB=2\n", PASSPHRASE, base_dir=store)
    summary = report.summary()
    assert "added" in summary
    assert "dev" in summary
