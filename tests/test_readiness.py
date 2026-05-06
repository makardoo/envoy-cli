"""Tests for envoy_cli.readiness."""
import pytest
from envoy_cli.readiness import (
    ReadinessError,
    VALID_STATES,
    set_readiness,
    get_readiness,
    remove_readiness,
    list_readiness,
    _readiness_path,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_readiness(base):
    set_readiness(base, "prod", "ready")
    record = get_readiness(base, "prod")
    assert record["state"] == "ready"


def test_set_creates_file(base):
    set_readiness(base, "staging", "pending")
    assert _readiness_path(base).exists()


def test_get_missing_raises(base):
    with pytest.raises(ReadinessError, match="No readiness record"):
        get_readiness(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(ReadinessError, match="must not be empty"):
        set_readiness(base, "", "ready")


def test_set_invalid_state_raises(base):
    with pytest.raises(ReadinessError, match="Invalid state"):
        set_readiness(base, "dev", "unknown_state")


def test_set_with_reason(base):
    set_readiness(base, "dev", "blocked", reason="Waiting for secrets rotation")
    record = get_readiness(base, "dev")
    assert record["reason"] == "Waiting for secrets rotation"


def test_set_without_reason_defaults_empty(base):
    set_readiness(base, "dev", "not_ready")
    record = get_readiness(base, "dev")
    assert record["reason"] == ""


def test_remove_readiness(base):
    set_readiness(base, "dev", "ready")
    remove_readiness(base, "dev")
    with pytest.raises(ReadinessError):
        get_readiness(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(ReadinessError, match="No readiness record"):
        remove_readiness(base, "nonexistent")


def test_list_empty(base):
    assert list_readiness(base) == {}


def test_list_shows_all_entries(base):
    set_readiness(base, "prod", "ready")
    set_readiness(base, "staging", "pending", reason="CI running")
    result = list_readiness(base)
    assert "prod" in result
    assert "staging" in result
    assert result["staging"]["reason"] == "CI running"


def test_all_valid_states_accepted(base):
    for i, state in enumerate(VALID_STATES):
        set_readiness(base, f"env_{i}", state)
        assert get_readiness(base, f"env_{i}")["state"] == state


def test_overwrite_readiness(base):
    set_readiness(base, "prod", "pending")
    set_readiness(base, "prod", "ready", reason="All checks passed")
    record = get_readiness(base, "prod")
    assert record["state"] == "ready"
    assert record["reason"] == "All checks passed"
