"""Tests for envoy_cli.anomaly."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.anomaly import (
    scan_content,
    scan_env,
    AnomalyError,
    AnomalyFinding,
    AnomalyReport,
)
from envoy_cli.env_file import encrypt_env
from envoy_cli.storage import save_env


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def _seed(base: Path, name: str, content: str, passphrase: str = "pw") -> None:
    encrypted = encrypt_env(content, passphrase)
    save_env(name, encrypted, base_dir=base)


# ---------------------------------------------------------------------------
# scan_content
# ---------------------------------------------------------------------------

def test_scan_content_clean_returns_no_findings() -> None:
    content = "API_URL=https://example.com\nDEBUG=false\n"
    report = scan_content(content, env_name="prod")
    assert report.clean
    assert report.env_name == "prod"


def test_scan_content_detects_placeholder() -> None:
    content = "SECRET_KEY=CHANGEME\n"
    report = scan_content(content)
    assert not report.clean
    keys = [f.key for f in report.findings]
    assert "SECRET_KEY" in keys
    finding = next(f for f in report.findings if f.key == "SECRET_KEY")
    assert finding.severity == "high"
    assert "placeholder" in finding.reason


def test_scan_content_detects_localhost() -> None:
    content = "DB_HOST=localhost\n"
    report = scan_content(content)
    assert not report.clean
    finding = report.findings[0]
    assert finding.severity == "low"
    assert "localhost" in finding.reason


def test_scan_content_detects_long_value() -> None:
    content = f"BLOB={'x' * 600}\n"
    report = scan_content(content)
    assert not report.clean
    assert any("length" in f.reason for f in report.findings)


def test_scan_content_detects_high_entropy() -> None:
    # A base64-like random string has high entropy
    value = "aB3dEfGhIjKlMnOpQrStUvWxYz012345"
    content = f"TOKEN={value}\n"
    report = scan_content(content)
    assert not report.clean
    assert any("entropy" in f.reason for f in report.findings)


def test_scan_content_ignores_comments_and_blanks() -> None:
    content = "# comment\n\nNAME=alice\n"
    report = scan_content(content)
    assert report.clean


def test_summary_clean() -> None:
    report = AnomalyReport(env_name="dev")
    assert "no anomalies" in report.summary()


def test_summary_with_findings() -> None:
    report = AnomalyReport(env_name="dev")
    report.findings.append(AnomalyFinding("KEY", "placeholder value detected", "high"))
    summary = report.summary()
    assert "HIGH" in summary
    assert "KEY" in summary


# ---------------------------------------------------------------------------
# scan_env
# ---------------------------------------------------------------------------

def test_scan_env_clean(base: Path) -> None:
    _seed(base, "dev", "API_URL=https://example.com\n")
    report = scan_env("dev", "pw", base_dir=base)
    assert report.clean


def test_scan_env_detects_placeholder(base: Path) -> None:
    _seed(base, "staging", "SECRET=CHANGEME\n")
    report = scan_env("staging", "pw", base_dir=base)
    assert not report.clean


def test_scan_env_raises_if_not_found(base: Path) -> None:
    with pytest.raises(AnomalyError, match="not found"):
        scan_env("ghost", "pw", base_dir=base)


def test_scan_env_raises_on_empty_name(base: Path) -> None:
    with pytest.raises(AnomalyError):
        scan_env("", "pw", base_dir=base)
