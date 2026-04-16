import pytest
from click.testing import CliRunner
from envoy_cli.cli_pin import pin_group
import envoy_cli.cli_pin as cli_pin_module


@pytest.fixture
def runner(tmp_path, monkeypatch):
    monkeypatch.setattr(cli_pin_module, "_base_dir", str(tmp_path))
    return CliRunner()


def test_set_pin(runner):
    result = runner.invoke(pin_group, ["set", "prod", "snap-abc"])
    assert result.exit_code == 0
    assert "Pinned" in result.output


def test_set_pin_with_label(runner):
    result = runner.invoke(pin_group, ["set", "prod", "snap-abc", "--label", "v2"])
    assert result.exit_code == 0


def test_show_pin(runner):
    runner.invoke(pin_group, ["set", "prod", "snap-abc", "--label", "v1"])
    result = runner.invoke(pin_group, ["show", "prod"])
    assert result.exit_code == 0
    assert "snap-abc" in result.output
    assert "v1" in result.output


def test_show_missing_exits_nonzero(runner):
    result = runner.invoke(pin_group, ["show", "ghost"])
    assert result.exit_code != 0


def test_remove_pin(runner):
    runner.invoke(pin_group, ["set", "prod", "snap-abc"])
    result = runner.invoke(pin_group, ["remove", "prod"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing_exits_nonzero(runner):
    result = runner.invoke(pin_group, ["remove", "ghost"])
    assert result.exit_code != 0


def test_list_empty(runner):
    result = runner.invoke(pin_group, ["list"])
    assert result.exit_code == 0
    assert "No pins" in result.output


def test_list_shows_entries(runner):
    runner.invoke(pin_group, ["set", "prod", "snap-1"])
    runner.invoke(pin_group, ["set", "staging", "snap-2", "--label", "beta"])
    result = runner.invoke(pin_group, ["list"])
    assert "prod" in result.output
    assert "staging" in result.output
    assert "beta" in result.output
