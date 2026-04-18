import pytest
from click.testing import CliRunner
from envoy_cli.group import (
    GroupError,
    add_to_group,
    remove_from_group,
    list_group,
    list_all_groups,
    delete_group,
)
from envoy_cli.cli_group import group_group


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_add_and_list(base):
    add_to_group(base, "team-a", "production")
    add_to_group(base, "team-a", "staging")
    assert list_group(base, "team-a") == ["production", "staging"]


def test_add_creates_file(base):
    import os
    add_to_group(base, "g1", "env1")
    assert os.path.exists(os.path.join(base, "groups.json"))


def test_add_duplicate_not_duplicated(base):
    add_to_group(base, "g", "env1")
    add_to_group(base, "g", "env1")
    assert list_group(base, "g").count("env1") == 1


def test_add_empty_group_raises(base):
    with pytest.raises(GroupError):
        add_to_group(base, "", "env1")


def test_add_empty_env_raises(base):
    with pytest.raises(GroupError):
        add_to_group(base, "g", "")


def test_remove_from_group(base):
    add_to_group(base, "g", "env1")
    add_to_group(base, "g", "env2")
    remove_from_group(base, "g", "env1")
    assert "env1" not in list_group(base, "g")


def test_remove_last_member_deletes_group(base):
    add_to_group(base, "g", "only")
    remove_from_group(base, "g", "only")
    assert "g" not in list_all_groups(base)


def test_remove_missing_raises(base):
    with pytest.raises(GroupError):
        remove_from_group(base, "g", "nonexistent")


def test_list_missing_group_raises(base):
    with pytest.raises(GroupError):
        list_group(base, "nope")


def test_delete_group(base):
    add_to_group(base, "g", "env1")
    delete_group(base, "g")
    assert "g" not in list_all_groups(base)


def test_delete_missing_raises(base):
    with pytest.raises(GroupError):
        delete_group(base, "ghost")


def test_list_all_empty(base):
    assert list_all_groups(base) == {}


# CLI tests
@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy_cli.cli_group._base_dir", str(tmp_path))
    return CliRunner(), tmp_path


def test_cli_add_and_list(runner):
    r, _ = runner
    result = r.invoke(group_group, ["add", "mygroup", "prod"])
    assert result.exit_code == 0
    result = r.invoke(group_group, ["list", "mygroup"])
    assert "prod" in result.output


def test_cli_delete(runner):
    r, _ = runner
    r.invoke(group_group, ["add", "g", "e"])
    result = r.invoke(group_group, ["delete", "g"])
    assert result.exit_code == 0
    assert "Deleted" in result.output


def test_cli_list_all_empty(runner):
    r, _ = runner
    result = r.invoke(group_group, ["list"])
    assert "No groups" in result.output
