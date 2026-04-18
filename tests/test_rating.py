"""Tests for envoy_cli.rating."""
import pytest
from envoy_cli.rating import (
    RatingError,
    set_rating,
    get_rating,
    remove_rating,
    list_ratings,
    _ratings_path,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_rating(base):
    set_rating(base, "production", 5)
    assert get_rating(base, "production") == 5


def test_set_creates_file(base):
    set_rating(base, "staging", 3)
    assert _ratings_path(base).exists()


def test_get_missing_raises(base):
    with pytest.raises(RatingError, match="No rating found"):
        get_rating(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(RatingError, match="must not be empty"):
        set_rating(base, "", 3)


def test_set_invalid_stars_low(base):
    with pytest.raises(RatingError, match="between 1 and 5"):
        set_rating(base, "dev", 0)


def test_set_invalid_stars_high(base):
    with pytest.raises(RatingError, match="between 1 and 5"):
        set_rating(base, "dev", 6)


def test_overwrite_rating(base):
    set_rating(base, "dev", 2)
    set_rating(base, "dev", 4)
    assert get_rating(base, "dev") == 4


def test_remove_rating(base):
    set_rating(base, "dev", 3)
    remove_rating(base, "dev")
    with pytest.raises(RatingError):
        get_rating(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(RatingError, match="No rating found"):
        remove_rating(base, "ghost")


def test_list_ratings(base):
    set_rating(base, "prod", 5)
    set_rating(base, "staging", 3)
    result = list_ratings(base)
    assert result == {"prod": 5, "staging": 3}


def test_list_ratings_empty(base):
    assert list_ratings(base) == {}
