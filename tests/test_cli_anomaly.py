"""Tests for envoy_cli.cli_anomaly."""
from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envoy_cli.cli_anomaly import anomaly_group
from envoy_cli.env_file import encrypt_env
from envoy_cli.storage import save_env


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    return tmp_path


def _seed(base: Path, name: str, content: str, passphrase: str = "pw") -> None:
    encrypted = encrypt_env(content, passphrase)
    save_env(name, encrypted, base_dir=base)


def test_scan_clean_env(runner: CliRunner, base: Path) -> None:
    _seed(base, "dev", "API_URL=https://example.com\n")
    result = runner.invoke(
        anomaly_group,
        ["scan", "dev", "--passphrase", "pw", "--base-dir", str(base)],
    )
    assert result.exit_code == 0
    assert "no anomalies" in result.output


def test_scan_dirty_env_exits_nonzero(runner: CliRunner, base: Path) -> None:
    _seed(base, "staging", "SECRET=CHANGEME\n")
    result = runner.invoke(
        anomaly_group,
        ["scan", "staging", "--passphrase", "pw", "--base-dir", str(base)],
    )
    assert result.exit_code == 2
    assert "HIGH" in result.output


def test_scan_missing_env_exits_nonzero(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(
        anomaly_group,
        ["scan", "ghost", "--passphrase", "pw", "--base-dir", str(base)],
    )
    assert result.exit_code == 1
    assert "Error" in result.output


def test_scan_all_empty(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(
        anomaly_group,
        ["scan-all", "--passphrase", "pw", "--base-dir", str(base)],
    )
    assert result.exit_code == 0
    assert "No environments" in result.output


def test_scan_all_reports_issues(runner: CliRunner, base: Path) -> None:
    _seed(base, "prod", "DB_HOST=localhost\n")
    _seed(base, "dev", "NAME=alice\n")
    result = runner.invoke(
        anomaly_group,
        ["scan-all", "--passphrase", "pw", "--base-dir", str(base)],
    )
    assert result.exit_code == 2
    assert "prod" in result.output
    assert "dev" in result.output
