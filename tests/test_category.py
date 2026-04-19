"""Tests for envoy_cli.category."""
import pytest
from pathlib import Path
from envoy_cli.category import (
    CategoryError,
    set_category,
    get_category,
    remove_category,
    list_by_category,
    list_all_categories,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_category(base):
    set_category(base, "prod", "production")
    assert get_category(base, "prod") == "production"


def test_set_creates_file(base):
    set_category(base, "staging", "staging")
    assert (Path(base) / "categories.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(CategoryError, match="No category"):
        get_category(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(CategoryError):
        set_category(base, "", "production")


def test_set_empty_category_raises(base):
    with pytest.raises(CategoryError):
        set_category(base, "prod", "")


def test_remove_category(base):
    set_category(base, "prod", "production")
    remove_category(base, "prod")
    with pytest.raises(CategoryError):
        get_category(base, "prod")


def test_remove_missing_raises(base):
    with pytest.raises(CategoryError):
        remove_category(base, "ghost")


def test_list_by_category(base):
    set_category(base, "prod", "production")
    set_category(base, "prod2", "production")
    set_category(base, "dev", "development")
    result = list_by_category(base, "production")
    assert set(result) == {"prod", "prod2"}


def test_list_by_category_empty(base):
    assert list_by_category(base, "nonexistent") == []


def test_list_all_categories(base):
    set_category(base, "prod", "production")
    set_category(base, "dev", "development")
    data = list_all_categories(base)
    assert data["prod"] == "production"
    assert data["dev"] == "development"


def test_overwrite_category(base):
    set_category(base, "prod", "production")
    set_category(base, "prod", "staging")
    assert get_category(base, "prod") == "staging"
