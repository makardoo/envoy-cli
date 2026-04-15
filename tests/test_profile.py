"""Tests for envoy_cli.profile."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.cli_profile import profile_group
from envoy_cli.profile import (
    ProfileError,
    apply_profile,
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)


@pytest.fixture()
def base(tmp_path):
    return tmp_path


# --- unit tests ---

def test_save_and_load_profile(base):
    save_profile("dev", {"DEBUG": "1", "LOG": "verbose"}, base_dir=base)
    data = load_profile("dev", base_dir=base)
    assert data == {"DEBUG": "1", "LOG": "verbose"}


def test_save_creates_profiles_dir(base):
    save_profile("prod", {"DEBUG": "0"}, base_dir=base)
    assert (base / "profiles" / "prod.json").exists()


def test_load_raises_if_not_found(base):
    with pytest.raises(ProfileError, match="not found"):
        load_profile("ghost", base_dir=base)


def test_save_empty_name_raises(base):
    with pytest.raises(ProfileError, match="empty"):
        save_profile("", {"K": "V"}, base_dir=base)


def test_list_profiles_returns_sorted(base):
    save_profile("zebra", {}, base_dir=base)
    save_profile("alpha", {}, base_dir=base)
    save_profile("beta", {}, base_dir=base)
    assert list_profiles(base_dir=base) == ["alpha", "beta", "zebra"]


def test_list_profiles_empty_dir(base):
    assert list_profiles(base_dir=base) == []


def test_delete_profile(base):
    save_profile("tmp", {"X": "1"}, base_dir=base)
    delete_profile("tmp", base_dir=base)
    assert list_profiles(base_dir=base) == []


def test_delete_profile_raises_if_missing(base):
    with pytest.raises(ProfileError, match="not found"):
        delete_profile("nope", base_dir=base)


def test_apply_profile_merges_overrides(base):
    save_profile("override", {"B": "new_b", "C": "new_c"}, base_dir=base)
    result = apply_profile({"A": "a", "B": "old_b"}, "override", base_dir=base)
    assert result == {"A": "a", "B": "new_b", "C": "new_c"}


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_and_list(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(profile_group, ["set", "ci", "CI=true", "LOG=info"])
    assert result.exit_code == 0
    assert "saved" in result.output


def test_cli_show(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(profile_group, ["set", "ci", "CI=true"])
    result = runner.invoke(profile_group, ["show", "ci"])
    assert result.exit_code == 0
    assert "CI" in result.output


def test_cli_delete(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(profile_group, ["set", "temp", "X=1"])
    result = runner.invoke(profile_group, ["delete", "temp"])
    assert result.exit_code == 0
    assert "deleted" in result.output


def test_cli_set_invalid_assignment(runner):
    result = runner.invoke(profile_group, ["set", "bad", "NOEQUALSSIGN"])
    assert result.exit_code != 0
