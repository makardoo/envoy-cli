"""Tests for envoy_cli.namespace."""
import pytest
from pathlib import Path
from click.testing import CliRunner
from envoy_cli.namespace import (
    NamespaceError,
    assign_namespace,
    get_namespace,
    remove_namespace,
    list_by_namespace,
    list_all_namespaces,
)
from envoy_cli.cli_namespace import namespace_group


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_assign_and_get(base):
    assign_namespace(base, "prod", "team-a")
    assert get_namespace(base, "prod") == "team-a"


def test_assign_creates_file(base):
    assign_namespace(base, "staging", "team-b")
    assert (Path(base) / "namespaces.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(NamespaceError, match="No namespace"):
        get_namespace(base, "unknown")


def test_assign_empty_env_raises(base):
    with pytest.raises(NamespaceError):
        assign_namespace(base, "", "team-a")


def test_assign_empty_namespace_raises(base):
    with pytest.raises(NamespaceError):
        assign_namespace(base, "prod", "")


def test_remove_namespace(base):
    assign_namespace(base, "prod", "team-a")
    remove_namespace(base, "prod")
    with pytest.raises(NamespaceError):
        get_namespace(base, "prod")


def test_remove_missing_raises(base):
    with pytest.raises(NamespaceError):
        remove_namespace(base, "ghost")


def test_list_by_namespace(base):
    assign_namespace(base, "prod", "team-a")
    assign_namespace(base, "staging", "team-a")
    assign_namespace(base, "dev", "team-b")
    result = list_by_namespace(base, "team-a")
    assert result == ["prod", "staging"]


def test_list_all_namespaces(base):
    assign_namespace(base, "prod", "team-a")
    assign_namespace(base, "dev", "team-b")
    mapping = list_all_namespaces(base)
    assert "team-a" in mapping
    assert mapping["team-a"] == ["prod"]


# CLI tests
@pytest.fixture
def runner():
    return CliRunner()


def test_cli_assign(runner, base):
    r = runner.invoke(namespace_group, ["assign", "prod", "team-x", "--base-dir", base])
    assert r.exit_code == 0
    assert "team-x" in r.output


def test_cli_show(runner, base):
    assign_namespace(base, "prod", "team-x")
    r = runner.invoke(namespace_group, ["show", "prod", "--base-dir", base])
    assert r.exit_code == 0
    assert "team-x" in r.output


def test_cli_show_missing_exits_nonzero(runner, base):
    r = runner.invoke(namespace_group, ["show", "nope", "--base-dir", base])
    assert r.exit_code != 0


def test_cli_list(runner, base):
    assign_namespace(base, "prod", "ns1")
    assign_namespace(base, "dev", "ns1")
    r = runner.invoke(namespace_group, ["list", "--base-dir", base])
    assert r.exit_code == 0
    assert "ns1" in r.output
