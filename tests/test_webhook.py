"""Tests for envoy_cli.webhook."""
import json
import pytest
from unittest.mock import patch, MagicMock
from envoy_cli.webhook import (
    register_webhook, remove_webhook, list_webhooks, fire_webhook, notify, WebhookError
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_register_creates_file(base):
    register_webhook(base, "https://example.com/hook", ["push"])
    hooks = list_webhooks(base)
    assert len(hooks) == 1
    assert hooks[0].url == "https://example.com/hook"


def test_register_with_label(base):
    register_webhook(base, "https://a.com", [], label="my-hook")
    assert list_webhooks(base)[0].label == "my-hook"


def test_register_duplicate_raises(base):
    register_webhook(base, "https://a.com", [])
    with pytest.raises(WebhookError, match="already registered"):
        register_webhook(base, "https://a.com", [])


def test_register_empty_url_raises(base):
    with pytest.raises(WebhookError, match="URL must not be empty"):
        register_webhook(base, "", [])


def test_remove_webhook(base):
    register_webhook(base, "https://a.com", [])
    remove_webhook(base, "https://a.com")
    assert list_webhooks(base) == []


def test_remove_missing_raises(base):
    with pytest.raises(WebhookError, match="not found"):
        remove_webhook(base, "https://missing.com")


def test_list_empty(base):
    assert list_webhooks(base) == []


def test_fire_webhook_success():
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        status = fire_webhook("https://example.com", {"event": "push"})
    assert status == 200


def test_fire_webhook_failure_raises():
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("conn refused")):
        with pytest.raises(WebhookError, match="Failed to fire"):
            fire_webhook("https://bad.url", {})


def test_notify_fires_matching_events(base):
    register_webhook(base, "https://a.com", ["push"])
    register_webhook(base, "https://b.com", ["pull"])
    with patch("envoy_cli.webhook.fire_webhook") as mock_fire:
        fired = notify(base, "push", {"env": "prod"})
    assert "https://a.com" in fired
    assert "https://b.com" not in fired


def test_notify_wildcard_fires_all(base):
    register_webhook(base, "https://all.com", [])  # empty = all events
    with patch("envoy_cli.webhook.fire_webhook") as mock_fire:
        fired = notify(base, "push", {})
    assert "https://all.com" in fired
