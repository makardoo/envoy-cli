import pytest
from pathlib import Path
from envoy_cli.label import (
    add_label, remove_label, get_labels, list_all, find_by_label, LabelError
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_add_and_get_label(base):
    add_label(base, "prod", "critical")
    assert "critical" in get_labels(base, "prod")


def test_add_creates_file(base):
    add_label(base, "staging", "review")
    assert (Path(base) / ".envoy" / "labels.json").exists()


def test_add_duplicate_not_duplicated(base):
    add_label(base, "prod", "critical")
    add_label(base, "prod", "critical")
    assert get_labels(base, "prod").count("critical") == 1


def test_add_multiple_labels(base):
    add_label(base, "prod", "critical")
    add_label(base, "prod", "reviewed")
    labels = get_labels(base, "prod")
    assert "critical" in labels
    assert "reviewed" in labels


def test_remove_label(base):
    add_label(base, "prod", "critical")
    remove_label(base, "prod", "critical")
    assert "critical" not in get_labels(base, "prod")


def test_remove_missing_label_raises(base):
    with pytest.raises(LabelError):
        remove_label(base, "prod", "nonexistent")


def test_get_labels_missing_env_returns_empty(base):
    assert get_labels(base, "ghost") == []


def test_list_all_returns_all(base):
    add_label(base, "prod", "critical")
    add_label(base, "staging", "review")
    result = list_all(base)
    assert "prod" in result
    assert "staging" in result


def test_find_by_label(base):
    add_label(base, "prod", "critical")
    add_label(base, "staging", "critical")
    add_label(base, "dev", "wip")
    found = find_by_label(base, "critical")
    assert "prod" in found
    assert "staging" in found
    assert "dev" not in found


def test_add_empty_name_raises(base):
    with pytest.raises(LabelError):
        add_label(base, "", "critical")


def test_add_empty_label_raises(base):
    with pytest.raises(LabelError):
        add_label(base, "prod", "")
