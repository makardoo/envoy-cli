import pytest
import os
from envoy_cli.pin import pin_env, get_pin, remove_pin, list_pins, PinError


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_pin_and_get(base):
    pin_env(base, "production", "snap-abc123")
    info = get_pin(base, "production")
    assert info["snapshot_id"] == "snap-abc123"
    assert info["label"] == ""


def test_pin_with_label(base):
    pin_env(base, "staging", "snap-xyz", label="release-1.0")
    info = get_pin(base, "staging")
    assert info["label"] == "release-1.0"


def test_pin_creates_file(base):
    pin_env(base, "dev", "snap-001")
    assert os.path.exists(os.path.join(base, "pins.json"))


def test_get_missing_raises(base):
    with pytest.raises(PinError, match="No pin found"):
        get_pin(base, "nonexistent")


def test_pin_empty_name_raises(base):
    with pytest.raises(PinError):
        pin_env(base, "", "snap-001")


def test_pin_empty_snapshot_raises(base):
    with pytest.raises(PinError):
        pin_env(base, "production", "")


def test_remove_pin(base):
    pin_env(base, "production", "snap-001")
    remove_pin(base, "production")
    with pytest.raises(PinError):
        get_pin(base, "production")


def test_remove_missing_raises(base):
    with pytest.raises(PinError, match="No pin found"):
        remove_pin(base, "ghost")


def test_list_pins_empty(base):
    assert list_pins(base) == []


def test_list_pins_multiple(base):
    pin_env(base, "prod", "snap-1", label="v1")
    pin_env(base, "staging", "snap-2")
    result = list_pins(base)
    names = [r["env_name"] for r in result]
    assert "prod" in names
    assert "staging" in names
    assert len(result) == 2


def test_overwrite_pin(base):
    pin_env(base, "prod", "snap-old")
    pin_env(base, "prod", "snap-new")
    info = get_pin(base, "prod")
    assert info["snapshot_id"] == "snap-new"
