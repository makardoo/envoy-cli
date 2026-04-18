"""Tests for envoy_cli.favorite."""

import pytest

from envoy_cli.favorite import (
    FavoriteError,
    add_favorite,
    is_favorite,
    list_favorites,
    remove_favorite,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_add_and_list(base):
    add_favorite(base, "production")
    add_favorite(base, "staging")
    assert list_favorites(base) == ["production", "staging"]


def test_add_creates_file(base, tmp_path):
    add_favorite(base, "dev")
    assert (tmp_path / "favorites.json").exists()


def test_add_duplicate_raises(base):
    add_favorite(base, "production")
    with pytest.raises(FavoriteError, match="already a favorite"):
        add_favorite(base, "production")


def test_add_empty_name_raises(base):
    with pytest.raises(FavoriteError, match="must not be empty"):
        add_favorite(base, "")


def test_remove_favorite(base):
    add_favorite(base, "staging")
    remove_favorite(base, "staging")
    assert list_favorites(base) == []


def test_remove_missing_raises(base):
    with pytest.raises(FavoriteError, match="not a favorite"):
        remove_favorite(base, "ghost")


def test_is_favorite_true(base):
    add_favorite(base, "prod")
    assert is_favorite(base, "prod") is True


def test_is_favorite_false(base):
    assert is_favorite(base, "prod") is False


def test_list_empty(base):
    assert list_favorites(base) == []


def test_order_preserved(base):
    for name in ["c", "a", "b"]:
        add_favorite(base, name)
    assert list_favorites(base) == ["c", "a", "b"]
