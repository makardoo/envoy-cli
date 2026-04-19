import pytest
from envoy_cli.pipeline import (
    create_pipeline, get_pipeline, delete_pipeline,
    list_pipelines, update_pipeline, PipelineError,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_create_and_get(base):
    create_pipeline(base, "deploy", ["validate", "push", "notify"])
    steps = get_pipeline(base, "deploy")
    assert steps == ["validate", "push", "notify"]


def test_create_creates_file(base):
    from pathlib import Path
    create_pipeline(base, "p1", ["a"])
    assert (Path(base) / "pipelines.json").exists()


def test_create_duplicate_raises(base):
    create_pipeline(base, "p", ["a"])
    with pytest.raises(PipelineError, match="already exists"):
        create_pipeline(base, "p", ["b"])


def test_create_empty_name_raises(base):
    with pytest.raises(PipelineError, match="empty"):
        create_pipeline(base, "", ["a"])


def test_create_empty_steps_raises(base):
    with pytest.raises(PipelineError, match="at least one step"):
        create_pipeline(base, "p", [])


def test_get_missing_raises(base):
    with pytest.raises(PipelineError, match="not found"):
        get_pipeline(base, "ghost")


def test_list_empty(base):
    assert list_pipelines(base) == []


def test_list_returns_names(base):
    create_pipeline(base, "a", ["x"])
    create_pipeline(base, "b", ["y"])
    names = list_pipelines(base)
    assert set(names) == {"a", "b"}


def test_delete_pipeline(base):
    create_pipeline(base, "tmp", ["x"])
    delete_pipeline(base, "tmp")
    assert "tmp" not in list_pipelines(base)


def test_delete_missing_raises(base):
    with pytest.raises(PipelineError, match="not found"):
        delete_pipeline(base, "nope")


def test_update_pipeline(base):
    create_pipeline(base, "p", ["a", "b"])
    update_pipeline(base, "p", ["x", "y", "z"])
    assert get_pipeline(base, "p") == ["x", "y", "z"]


def test_update_missing_raises(base):
    with pytest.raises(PipelineError, match="not found"):
        update_pipeline(base, "ghost", ["a"])


def test_update_empty_steps_raises(base):
    create_pipeline(base, "p", ["a"])
    with pytest.raises(PipelineError, match="at least one step"):
        update_pipeline(base, "p", [])
