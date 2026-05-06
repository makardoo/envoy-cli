"""Tests for envoy_cli.classification."""
import pytest

from envoy_cli.classification import (
    ClassificationError,
    VALID_LEVELS,
    get_classification,
    list_classifications,
    remove_classification,
    set_classification,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_classification(base):
    set_classification(base, "production", "confidential")
    assert get_classification(base, "production") == "confidential"


def test_set_creates_file(base, tmp_path):
    set_classification(base, "staging", "internal")
    assert (tmp_path / "classifications.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(ClassificationError, match="No classification set"):
        get_classification(base, "ghost")


def test_set_empty_name_raises(base):
    with pytest.raises(ClassificationError, match="must not be empty"):
        set_classification(base, "", "public")


def test_get_empty_name_raises(base):
    with pytest.raises(ClassificationError, match="must not be empty"):
        get_classification(base, "")


def test_set_invalid_level_raises(base):
    with pytest.raises(ClassificationError, match="Invalid classification level"):
        set_classification(base, "dev", "top-secret")


def test_all_valid_levels_accepted(base):
    for level in VALID_LEVELS:
        set_classification(base, f"env-{level}", level)
        assert get_classification(base, f"env-{level}") == level


def test_overwrite_classification(base):
    set_classification(base, "dev", "public")
    set_classification(base, "dev", "restricted")
    assert get_classification(base, "dev") == "restricted"


def test_remove_classification(base):
    set_classification(base, "dev", "internal")
    remove_classification(base, "dev")
    with pytest.raises(ClassificationError):
        get_classification(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(ClassificationError, match="No classification set"):
        remove_classification(base, "nonexistent")


def test_list_classifications_empty(base):
    assert list_classifications(base) == {}


def test_list_classifications_returns_all(base):
    set_classification(base, "prod", "restricted")
    set_classification(base, "staging", "confidential")
    result = list_classifications(base)
    assert result == {"prod": "restricted", "staging": "confidential"}
