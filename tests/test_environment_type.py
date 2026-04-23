"""Tests for envoy_cli.environment_type."""
import pytest
from pathlib import Path

from envoy_cli.environment_type import (
    EnvironmentTypeError,
    set_env_type,
    get_env_type,
    remove_env_type,
    list_env_types,
    _type_path,
)


@pytest.fixture()
def base(tmp_path: Path) -> str:
    return str(tmp_path)


def test_set_and_get_env_type(base):
    set_env_type(base, "myapp", "production")
    assert get_env_type(base, "myapp") == "production"


def test_set_creates_file(base):
    set_env_type(base, "myapp", "staging")
    assert _type_path(base).exists()


def test_get_missing_raises(base):
    with pytest.raises(EnvironmentTypeError, match="No type set"):
        get_env_type(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(EnvironmentTypeError, match="must not be empty"):
        set_env_type(base, "", "local")


def test_set_invalid_type_raises(base):
    with pytest.raises(EnvironmentTypeError, match="Invalid type"):
        set_env_type(base, "myapp", "unknown_env")


def test_remove_env_type(base):
    set_env_type(base, "myapp", "local")
    remove_env_type(base, "myapp")
    with pytest.raises(EnvironmentTypeError):
        get_env_type(base, "myapp")


def test_remove_missing_raises(base):
    with pytest.raises(EnvironmentTypeError, match="No type set"):
        remove_env_type(base, "ghost")


def test_list_env_types_empty(base):
    assert list_env_types(base) == {}


def test_list_env_types_returns_all(base):
    set_env_type(base, "app1", "local")
    set_env_type(base, "app2", "production")
    result = list_env_types(base)
    assert result == {"app1": "local", "app2": "production"}


def test_overwrite_existing_type(base):
    set_env_type(base, "myapp", "local")
    set_env_type(base, "myapp", "staging")
    assert get_env_type(base, "myapp") == "staging"


def test_all_valid_types_accepted(base):
    from envoy_cli.environment_type import VALID_TYPES
    for i, t in enumerate(sorted(VALID_TYPES)):
        set_env_type(base, f"env_{i}", t)
        assert get_env_type(base, f"env_{i}") == t
