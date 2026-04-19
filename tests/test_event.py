import pytest
from envoy_cli.event import (
    subscribe, unsubscribe, get_subscribers,
    list_all_subscriptions, EventError,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_subscribe_and_get(base):
    subscribe(base, "set", "notify.sh")
    assert "notify.sh" in get_subscribers(base, "set")


def test_subscribe_creates_file(base):
    from pathlib import Path
    subscribe(base, "push", "deploy.sh")
    assert (Path(base) / "events" / "subscriptions.json").exists()


def test_subscribe_duplicate_not_duplicated(base):
    subscribe(base, "set", "notify.sh")
    subscribe(base, "set", "notify.sh")
    assert get_subscribers(base, "set").count("notify.sh") == 1


def test_subscribe_multiple_handlers(base):
    subscribe(base, "set", "a.sh")
    subscribe(base, "set", "b.sh")
    subs = get_subscribers(base, "set")
    assert "a.sh" in subs
    assert "b.sh" in subs


def test_subscribe_invalid_event_raises(base):
    with pytest.raises(EventError, match="Unknown event"):
        subscribe(base, "invalid_event", "handler.sh")


def test_subscribe_empty_event_raises(base):
    with pytest.raises(EventError, match="must not be empty"):
        subscribe(base, "", "handler.sh")


def test_subscribe_empty_handler_raises(base):
    with pytest.raises(EventError, match="Handler must not be empty"):
        subscribe(base, "set", "")


def test_unsubscribe_removes_handler(base):
    subscribe(base, "set", "notify.sh")
    unsubscribe(base, "set", "notify.sh")
    assert "notify.sh" not in get_subscribers(base, "set")


def test_unsubscribe_not_subscribed_raises(base):
    with pytest.raises(EventError, match="not subscribed"):
        unsubscribe(base, "set", "ghost.sh")


def test_list_all_subscriptions(base):
    subscribe(base, "set", "a.sh")
    subscribe(base, "pull", "b.sh")
    all_subs = list_all_subscriptions(base)
    assert "a.sh" in all_subs["set"]
    assert "b.sh" in all_subs["pull"]


def test_get_subscribers_empty(base):
    assert get_subscribers(base, "set") == []
