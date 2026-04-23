"""Tests for envoy_cli.secret."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy_cli.secret import (
    scan_content,
    scan_env,
    SecretError,
    SecretFinding,
    ScanResult,
)
from envoy_cli.storage import save_env
from envoy_cli.env_file import encrypt_env


PASSPHRASE = "hunter2"


@pytest.fixture
def store(tmp_path):
    return tmp_path


def _seed(store: Path, env_name: str, content: str):
    encrypted = encrypt_env(content, PASSPHRASE)
    save_env(env_name, encrypted, base_dir=store)


# --- scan_content ---

def test_scan_content_clean_returns_no_findings():
    content = "DEBUG=true\nPORT=8080\n"
    result = scan_content(content, env_name="test")
    assert result.clean
    assert result.findings == []


def test_scan_content_detects_aws_key():
    content = "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n"
    result = scan_content(content)
    assert not result.clean
    assert any(f.rule == "aws-access-key" for f in result.findings)


def test_scan_content_detects_high_entropy():
    content = "SECRET=abcdefghijklmnopqrstuvwxyzABCDEFGH\n"
    result = scan_content(content)
    assert not result.clean


def test_scan_content_ignores_comments():
    content = "# AWS_KEY=AKIAIOSFODNN7EXAMPLE\nPORT=3000\n"
    result = scan_content(content)
    assert result.clean


def test_scan_content_ignores_blank_lines():
    content = "\n\nPORT=3000\n\n"
    result = scan_content(content)
    assert result.clean


def test_scan_content_finding_has_correct_line_number():
    content = "PORT=8080\nAWS_KEY=AKIAIOSFODNN7EXAMPLE\n"
    result = scan_content(content)
    assert result.findings[0].line == 2


def test_scan_content_detects_github_token():
    content = "GH_TOKEN=ghp_abcdefghijklmnopqrstuvwxyzABCDEFGH\n"
    result = scan_content(content)
    assert not result.clean
    assert any(f.rule == "github-token" for f in result.findings)


def test_finding_masked_value_hides_middle():
    finding = SecretFinding(key="K", value="abcdefgh", rule="test", line=1)
    masked = finding.masked_value()
    assert masked.startswith("ab")
    assert masked.endswith("gh")
    assert "****" in masked


def test_finding_masked_value_short():
    finding = SecretFinding(key="K", value="ab", rule="test", line=1)
    assert finding.masked_value() == "****"


# --- scan_env ---

def test_scan_env_clean(store):
    _seed(store, "myenv", "PORT=8080\nDEBUG=true\n")
    result = scan_env("myenv", PASSPHRASE, base_dir=store)
    assert result.clean
    assert result.env_name == "myenv"


def test_scan_env_finds_secret(store):
    _seed(store, "prod", "AWS_KEY=AKIAIOSFODNN7EXAMPLE\n")
    result = scan_env("prod", PASSPHRASE, base_dir=store)
    assert not result.clean


def test_scan_env_raises_if_not_found(store):
    with pytest.raises(SecretError, match="not found"):
        scan_env("missing", PASSPHRASE, base_dir=store)
