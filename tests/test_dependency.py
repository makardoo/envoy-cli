import pytest
from envoy_cli.dependency import (
    add_dependency,
    remove_dependency,
    get_dependencies,
    list_all_dependencies,
    detect_cycle,
    DependencyError,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_add_and_get_dependency(base):
    add_dependency(base, "staging", "base")
    assert get_dependencies(base, "staging") == ["base"]


def test_add_creates_file(base):
    from pathlib import Path
    add_dependency(base, "staging", "base")
    assert (Path(base) / ".envoy" / "dependencies.json").exists()


def test_add_duplicate_not_duplicated(base):
    add_dependency(base, "staging", "base")
    add_dependency(base, "staging", "base")
    assert get_dependencies(base, "staging").count("base") == 1


def test_add_multiple_dependencies(base):
    add_dependency(base, "prod", "base")
    add_dependency(base, "prod", "secrets")
    deps = get_dependencies(base, "prod")
    assert "base" in deps
    assert "secrets" in deps


def test_get_missing_returns_empty(base):
    assert get_dependencies(base, "nonexistent") == []


def test_list_all(base):
    add_dependency(base, "staging", "base")
    add_dependency(base, "prod", "base")
    all_deps = list_all_dependencies(base)
    assert "staging" in all_deps
    assert "prod" in all_deps


def test_remove_dependency(base):
    add_dependency(base, "staging", "base")
    remove_dependency(base, "staging", "base")
    assert get_dependencies(base, "staging") == []


def test_remove_missing_raises(base):
    with pytest.raises(DependencyError):
        remove_dependency(base, "staging", "base")


def test_add_self_dependency_raises(base):
    with pytest.raises(DependencyError):
        add_dependency(base, "staging", "staging")


def test_add_empty_name_raises(base):
    with pytest.raises(DependencyError):
        add_dependency(base, "", "base")


def test_add_empty_depends_on_raises(base):
    with pytest.raises(DependencyError):
        add_dependency(base, "staging", "")


def test_detect_cycle_direct(base):
    add_dependency(base, "b", "a")
    assert detect_cycle(base, "a", "b") is True


def test_detect_cycle_transitive(base):
    add_dependency(base, "b", "a")
    add_dependency(base, "c", "b")
    assert detect_cycle(base, "a", "c") is True


def test_detect_no_cycle(base):
    add_dependency(base, "b", "a")
    assert detect_cycle(base, "c", "b") is False
