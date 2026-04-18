import pytest
from envoy_cli.comment import set_comment, get_comment, remove_comment, list_comments, CommentError


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_comment(base):
    set_comment(base, "prod", "DB_HOST", "Primary database host")
    assert get_comment(base, "prod", "DB_HOST") == "Primary database host"


def test_set_creates_file(base, tmp_path):
    set_comment(base, "prod", "KEY", "some note")
    assert (tmp_path / "prod.comments.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(CommentError, match="No comment"):
        get_comment(base, "prod", "MISSING")


def test_remove_comment(base):
    set_comment(base, "prod", "API_KEY", "secret key")
    remove_comment(base, "prod", "API_KEY")
    with pytest.raises(CommentError):
        get_comment(base, "prod", "API_KEY")


def test_remove_missing_raises(base):
    with pytest.raises(CommentError, match="No comment"):
        remove_comment(base, "prod", "GHOST")


def test_list_comments_empty(base):
    result = list_comments(base, "staging")
    assert result == {}


def test_list_comments_returns_all(base):
    set_comment(base, "dev", "FOO", "foo note")
    set_comment(base, "dev", "BAR", "bar note")
    result = list_comments(base, "dev")
    assert result == {"FOO": "foo note", "BAR": "bar note"}


def test_set_empty_env_name_raises(base):
    with pytest.raises(CommentError, match="env_name"):
        set_comment(base, "", "KEY", "note")


def test_set_empty_key_raises(base):
    with pytest.raises(CommentError, match="key"):
        set_comment(base, "prod", "", "note")


def test_overwrite_comment(base):
    set_comment(base, "prod", "HOST", "old")
    set_comment(base, "prod", "HOST", "new")
    assert get_comment(base, "prod", "HOST") == "new"
