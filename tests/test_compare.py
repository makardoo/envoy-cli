"""Tests for envoy_cli.compare."""
import pytest
from unittest.mock import patch

from envoy_cli.compare import compare_envs, format_compare, CompareError


PASSPHRASE = "test-secret"


@pytest.fixture()
def store(tmp_path):
    """Seed two envs into a temporary store."""
    from envoy_cli.storage import save_env
    from envoy_cli.env_file import encrypt_env

    base = str(tmp_path)

    content_a = "KEY_A=hello\nSHARED=same\nDIFF=aaa\n"
    content_b = "KEY_B=world\nSHARED=same\nDIFF=bbb\n"

    save_env("env_a", encrypt_env(content_a, PASSPHRASE), base_dir=base)
    save_env("env_b", encrypt_env(content_b, PASSPHRASE), base_dir=base)

    return base


def test_compare_only_in_a(store):
    result = compare_envs("env_a", "env_b", PASSPHRASE, base_dir=store)
    assert "KEY_A" in result.only_in_a
    assert "KEY_B" not in result.only_in_a


def test_compare_only_in_b(store):
    result = compare_envs("env_a", "env_b", PASSPHRASE, base_dir=store)
    assert "KEY_B" in result.only_in_b
    assert "KEY_A" not in result.only_in_b


def test_compare_different_values(store):
    result = compare_envs("env_a", "env_b", PASSPHRASE, base_dir=store)
    assert "DIFF" in result.different_values


def test_compare_same_keys(store):
    result = compare_envs("env_a", "env_b", PASSPHRASE, base_dir=store)
    assert "SHARED" in result.same_keys


def test_compare_separate_passphrases(store):
    result = compare_envs("env_a", "env_b", PASSPHRASE, passphrase_b=PASSPHRASE, base_dir=store)
    assert isinstance(result.same_keys, list)


def test_compare_missing_env_raises(store):
    with pytest.raises(CompareError, match="ghost"):
        compare_envs("env_a", "ghost", PASSPHRASE, base_dir=store)


def test_format_compare_no_diff(store):
    from envoy_cli.compare import CompareResult
    result = CompareResult(only_in_a=[], only_in_b=[], different_values=[], same_keys=["X"])
    out = format_compare(result, "a", "b")
    assert out == "(no differences)"


def test_format_compare_shows_markers(store):
    from envoy_cli.compare import CompareResult
    result = CompareResult(only_in_a=["A"], only_in_b=["B"], different_values=["C"], same_keys=[])
    out = format_compare(result, "env_a", "env_b")
    assert "< A" in out
    assert "> B" in out
    assert "~ C" in out


def test_format_compare_show_same(store):
    from envoy_cli.compare import CompareResult
    result = CompareResult(only_in_a=[], only_in_b=[], different_values=[], same_keys=["X"])
    out = format_compare(result, "a", "b", show_same=True)
    assert "= X" in out
