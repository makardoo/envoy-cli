import pytest
from pathlib import Path
from envoy_cli.tag import add_tag, remove_tag, get_tag, list_tags, TagError


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_add_and_get_tag(base):
    add_tag(base, "v1", "production", "/some/snapshot.json")
    info = get_tag(base, "v1")
    assert info["env"] == "production"
    assert info["ref"] == "/some/snapshot.json"


def test_add_creates_tags_file(base):
    add_tag(base, "stable", "staging", "abc123")
    assert (Path(base) / "tags.json").exists()


def test_get_missing_tag_raises(base):
    with pytest.raises(TagError, match="not found"):
        get_tag(base, "nonexistent")


def test_remove_tag(base):
    add_tag(base, "old", "dev", "ref1")
    remove_tag(base, "old")
    with pytest.raises(TagError):
        get_tag(base, "old")


def test_remove_missing_tag_raises(base):
    with pytest.raises(TagError, match="not found"):
        remove_tag(base, "ghost")


def test_list_tags_empty(base):
    assert list_tags(base) == []


def test_list_tags_returns_all(base):
    add_tag(base, "beta", "staging", "r2")
    add_tag(base, "alpha", "dev", "r1")
    tags = list_tags(base)
    assert len(tags) == 2
    names = [t["tag"] for t in tags]
    assert "alpha" in names
    assert "beta" in names


def test_add_empty_tag_raises(base):
    with pytest.raises(TagError, match="empty"):
        add_tag(base, "", "dev", "ref")


def test_add_empty_env_raises(base):
    with pytest.raises(TagError, match="empty"):
        add_tag(base, "v1", "", "ref")


def test_overwrite_existing_tag(base):
    add_tag(base, "latest", "prod", "old-ref")
    add_tag(base, "latest", "prod", "new-ref")
    info = get_tag(base, "latest")
    assert info["ref"] == "new-ref"
