"""Tests for envoy_cli.cli_rollback."""
from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner

from envoy_cli.cli_rollback import rollback_group
from envoy_cli.storage import save_env, load_env
from envoy_cli.snapshot import create_snapshot

PASSPHRASE = "cli-pass"
ENV_NAME = "staging"
ENV_CONTENT = "DB=postgres\nSECRET=abc\n"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def base(tmp_path: Path) -> Path:
    save_env(tmp_path, ENV_NAME, ENV_CONTENT, PASSPHRASE)
    return tmp_path


def test_list_empty(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(
        rollback_group, ["list", ENV_NAME, "--base-dir", str(base)]
    )
    assert result.exit_code == 0
    assert "No snapshots" in result.output


def test_list_shows_snapshots(runner: CliRunner, base: Path) -> None:
    create_snapshot(base, ENV_NAME, "snap-a", PASSPHRASE)
    result = runner.invoke(
        rollback_group, ["list", ENV_NAME, "--base-dir", str(base)]
    )
    assert result.exit_code == 0
    assert "snap-a" in result.output


def test_rollback_to_named_snapshot(runner: CliRunner, base: Path) -> None:
    create_snapshot(base, ENV_NAME, "v1", PASSPHRASE)
    save_env(base, ENV_NAME, "DB=changed\n", PASSPHRASE)
    result = runner.invoke(
        rollback_group,
        ["to", ENV_NAME, "v1", "--passphrase", PASSPHRASE, "--base-dir", str(base)],
    )
    assert result.exit_code == 0
    assert "v1" in result.output
    restored = load_env(base, ENV_NAME, PASSPHRASE)
    assert restored == ENV_CONTENT


def test_rollback_to_missing_snapshot_exits_nonzero(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(
        rollback_group,
        ["to", ENV_NAME, "ghost", "--passphrase", PASSPHRASE, "--base-dir", str(base)],
    )
    assert result.exit_code != 0


def test_rollback_latest(runner: CliRunner, base: Path) -> None:
    create_snapshot(base, ENV_NAME, "snap-latest", PASSPHRASE)
    save_env(base, ENV_NAME, "DB=changed\n", PASSPHRASE)
    result = runner.invoke(
        rollback_group,
        ["latest", ENV_NAME, "--passphrase", PASSPHRASE, "--base-dir", str(base)],
    )
    assert result.exit_code == 0
    assert "latest" in result.output.lower()
    restored = load_env(base, ENV_NAME, PASSPHRASE)
    assert restored == ENV_CONTENT


def test_rollback_latest_no_snapshots_exits_nonzero(runner: CliRunner, base: Path) -> None:
    result = runner.invoke(
        rollback_group,
        ["latest", ENV_NAME, "--passphrase", PASSPHRASE, "--base-dir", str(base)],
    )
    assert result.exit_code != 0
