import pytest
from click.testing import CliRunner
from envoy_cli.cli_event import event_group


@pytest.fixture
def runner():
    return CliRunner()


def test_subscribe(runner, tmp_path):
    result = runner.invoke(
        event_group, ["subscribe", "set", "notify.sh", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "Subscribed" in result.output


def test_subscribe_invalid_event_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        event_group, ["subscribe", "bad_event", "notify.sh", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_unsubscribe(runner, tmp_path):
    runner.invoke(event_group, ["subscribe", "set", "notify.sh", "--base-dir", str(tmp_path)])
    result = runner.invoke(
        event_group, ["unsubscribe", "set", "notify.sh", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code == 0
    assert "Unsubscribed" in result.output


def test_unsubscribe_missing_exits_nonzero(runner, tmp_path):
    result = runner.invoke(
        event_group, ["unsubscribe", "set", "ghost.sh", "--base-dir", str(tmp_path)]
    )
    assert result.exit_code != 0


def test_list_empty(runner, tmp_path):
    result = runner.invoke(event_group, ["list", "--base-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No subscriptions" in result.output


def test_list_shows_entries(runner, tmp_path):
    runner.invoke(event_group, ["subscribe", "push", "deploy.sh", "--base-dir", str(tmp_path)])
    result = runner.invoke(event_group, ["list", "--base-dir", str(tmp_path)])
    assert "push" in result.output
    assert "deploy.sh" in result.output


def test_list_events(runner):
    result = runner.invoke(event_group, ["events"])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "push" in result.output
