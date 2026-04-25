"""Tests for envoy_cli.lineage."""
import pytest
from envoy_cli.lineage import (
    LineageError,
    get_ancestors,
    get_children,
    get_parent,
    remove_parent,
    set_parent,
)


@pytest.fixture()
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_parent(base):
    set_parent(base, "staging", "production")
    assert get_parent(base, "staging") == "production"


def test_set_creates_file(base):
    import json
    from pathlib import Path

    set_parent(base, "dev", "staging")
    p = Path(base) / "lineage.json"
    assert p.exists()
    data = json.loads(p.read_text())
    assert data["dev"]["parent"] == "staging"


def test_get_missing_raises(base):
    with pytest.raises(LineageError, match="No parent set"):
        get_parent(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(LineageError):
        set_parent(base, "", "production")


def test_set_empty_parent_raises(base):
    with pytest.raises(LineageError):
        set_parent(base, "staging", "")


def test_self_parent_raises(base):
    with pytest.raises(LineageError, match="cannot be its own parent"):
        set_parent(base, "staging", "staging")


def test_remove_parent(base):
    set_parent(base, "staging", "production")
    remove_parent(base, "staging")
    with pytest.raises(LineageError):
        get_parent(base, "staging")


def test_remove_missing_parent_raises(base):
    with pytest.raises(LineageError, match="No parent set"):
        remove_parent(base, "staging")


def test_get_children_returns_correct_names(base):
    set_parent(base, "staging", "production")
    set_parent(base, "dev", "production")
    set_parent(base, "qa", "staging")
    children = get_children(base, "production")
    assert sorted(children) == ["dev", "staging"]


def test_get_children_empty(base):
    assert get_children(base, "production") == []


def test_get_ancestors_single(base):
    set_parent(base, "dev", "staging")
    assert get_ancestors(base, "dev") == ["staging"]


def test_get_ancestors_chain(base):
    set_parent(base, "dev", "staging")
    set_parent(base, "staging", "production")
    assert get_ancestors(base, "dev") == ["staging", "production"]


def test_get_ancestors_no_parent(base):
    assert get_ancestors(base, "production") == []


def test_overwrite_parent(base):
    set_parent(base, "dev", "staging")
    set_parent(base, "dev", "production")
    assert get_parent(base, "dev") == "production"
