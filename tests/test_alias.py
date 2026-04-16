import pytest
from pathlib import Path
from envoy_cli.alias import (
    set_alias, get_alias, remove_alias, list_aliases, AliasError
)


@pytest.fixture
def base(tmp_path):
    return tmp_path


def test_set_and_get_alias(base):
    set_alias(base, "prod", "myapp", "production")
    result = get_alias(base, "prod")
    assert result["env_name"] == "myapp"
    assert result["profile"] == "production"


def test_set_alias_default_profile(base):
    set_alias(base, "dev", "myapp")
    result = get_alias(base, "dev")
    assert result["profile"] == "default"


def test_set_creates_aliases_file(base):
    set_alias(base, "dev", "myapp")
    assert (base / "aliases.json").exists()


def test_get_missing_alias_raises(base):
    with pytest.raises(AliasError, match="not found"):
        get_alias(base, "nonexistent")


def test_set_empty_alias_raises(base):
    with pytest.raises(AliasError, match="empty"):
        set_alias(base, "", "myapp")


def test_set_empty_env_name_raises(base):
    with pytest.raises(AliasError, match="empty"):
        set_alias(base, "dev", "")


def test_remove_alias(base):
    set_alias(base, "staging", "myapp", "staging")
    remove_alias(base, "staging")
    with pytest.raises(AliasError):
        get_alias(base, "staging")


def test_remove_missing_alias_raises(base):
    with pytest.raises(AliasError, match="not found"):
        remove_alias(base, "ghost")


def test_list_aliases_empty(base):
    assert list_aliases(base) == {}


def test_list_aliases_returns_all(base):
    set_alias(base, "a", "app1")
    set_alias(base, "b", "app2", "prod")
    result = list_aliases(base)
    assert "a" in result
    assert "b" in result
    assert len(result) == 2


def test_overwrite_alias(base):
    set_alias(base, "dev", "app1")
    set_alias(base, "dev", "app2", "staging")
    result = get_alias(base, "dev")
    assert result["env_name"] == "app2"
    assert result["profile"] == "staging"
