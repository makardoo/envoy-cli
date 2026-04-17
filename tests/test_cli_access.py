import pytest
from click.testing import CliRunner
from envoy_cli.cli_access import access_group
from envoy_cli.access import set_permission
import envoy_cli.storage as storage_mod


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setattr(storage_mod, "get_env_dir", lambda: str(tmp_path))
    return CliRunner(), str(tmp_path)


def test_grant_readwrite(runner):
    r, base = runner
    result = r.invoke(access_group, ["grant", "prod", "alice"])
    assert result.exit_code == 0
    assert "read/write" in result.output


def test_grant_readonly(runner):
    r, base = runner
    result = r.invoke(access_group, ["grant", "prod", "alice", "--no-write"])
    assert result.exit_code == 0
    assert "read-only" in result.output


def test_revoke(runner):
    r, base = runner
    set_permission(base, "prod", "alice", True, True)
    result = r.invoke(access_group, ["revoke", "prod", "alice"])
    assert result.exit_code == 0
    assert "Revoked" in result.output


def test_revoke_missing_exits_nonzero(runner):
    r, _ = runner
    result = r.invoke(access_group, ["revoke", "prod", "ghost"])
    assert result.exit_code != 0


def test_show_empty(runner):
    r, _ = runner
    result = r.invoke(access_group, ["show", "prod"])
    assert result.exit_code == 0
    assert "No explicit" in result.output


def test_show_lists_profiles(runner):
    r, base = runner
    set_permission(base, "prod", "alice", True, True)
    set_permission(base, "prod", "bob", True, False)
    result = r.invoke(access_group, ["show", "prod"])
    assert "alice" in result.output
    assert "bob" in result.output


def test_check_allowed(runner):
    r, base = runner
    set_permission(base, "prod", "alice", True, True)
    result = r.invoke(access_group, ["check", "prod", "alice", "write"])
    assert result.exit_code == 0
    assert "allowed" in result.output


def test_check_denied_exits_nonzero(runner):
    r, base = runner
    set_permission(base, "prod", "alice", True, False)
    result = r.invoke(access_group, ["check", "prod", "alice", "write"])
    assert result.exit_code != 0
    assert "denied" in result.output
