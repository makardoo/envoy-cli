"""Tests for envoy_cli.merge."""
import pytest
from envoy_cli.merge import merge_dicts, merge_envs, MergeStrategy, MergeError
from envoy_cli.env_file import serialize_env, encrypt_env
from envoy_cli.storage import save_env


BASE = {"KEY1": "aaa", "KEY2": "bbb", "SHARED": "base_val"}
OTHER = {"KEY3": "ccc", "SHARED": "other_val"}


def test_merge_dicts_adds_missing_keys():
    result = merge_dicts(BASE, OTHER)
    assert result.merged["KEY3"] == "ccc"


def test_merge_dicts_ours_keeps_base_on_conflict():
    result = merge_dicts(BASE, OTHER, MergeStrategy.OURS)
    assert result.merged["SHARED"] == "base_val"


def test_merge_dicts_theirs_keeps_other_on_conflict():
    result = merge_dicts(BASE, OTHER, MergeStrategy.THEIRS)
    assert result.merged["SHARED"] == "other_val"


def test_merge_dicts_reports_conflicts():
    result = merge_dicts(BASE, OTHER)
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    assert conflict.key == "SHARED"
    assert conflict.base_value == "base_val"
    assert conflict.other_value == "other_val"


def test_merge_dicts_no_conflict_when_values_equal():
    result = merge_dicts({"A": "1"}, {"A": "1"})
    assert result.conflicts == []


def test_merge_dicts_union_keeps_all_keys():
    result = merge_dicts(BASE, OTHER, MergeStrategy.UNION)
    for key in list(BASE) + list(OTHER):
        assert key in result.merged


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path)


def _seed(name, data, passphrase, base_dir):
    plain = serialize_env(list(data.items()))
    encrypted = encrypt_env(plain, passphrase)
    save_env(name, encrypted, base_dir=base_dir)


def test_merge_envs_roundtrip(store):
    _seed("base", BASE, "secret", store)
    _seed("other", OTHER, "secret", store)
    result = merge_envs("base", "other", "secret", base_dir=store)
    assert "KEY1" in result.merged
    assert "KEY3" in result.merged


def test_merge_envs_raises_if_env_missing(store):
    _seed("base", BASE, "secret", store)
    with pytest.raises(MergeError, match="not found"):
        merge_envs("base", "ghost", "secret", base_dir=store)


def test_merge_envs_raises_if_base_missing(store):
    _seed("other", OTHER, "secret", store)
    with pytest.raises(MergeError, match="not found"):
        merge_envs("ghost", "other", "secret", base_dir=store)
