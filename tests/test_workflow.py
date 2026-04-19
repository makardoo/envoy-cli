import pytest
import os
from envoy_cli.workflow import (
    WorkflowError,
    create_workflow,
    get_workflow,
    update_workflow,
    delete_workflow,
    list_workflows,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_create_and_get(base):
    entry = create_workflow(base, "deploy", ["validate", "push", "notify"])
    assert entry["name"] == "deploy"
    assert entry["steps"] == ["validate", "push", "notify"]
    fetched = get_workflow(base, "deploy")
    assert fetched == entry


def test_create_creates_file(base):
    create_workflow(base, "ci", ["lint"])
    assert os.path.exists(os.path.join(base, "workflows.json"))


def test_create_duplicate_raises(base):
    create_workflow(base, "deploy", ["push"])
    with pytest.raises(WorkflowError, match="already exists"):
        create_workflow(base, "deploy", ["push"])


def test_create_empty_name_raises(base):
    with pytest.raises(WorkflowError, match="empty"):
        create_workflow(base, "", ["push"])


def test_create_empty_steps_raises(base):
    with pytest.raises(WorkflowError, match="at least one step"):
        create_workflow(base, "empty", [])


def test_get_missing_raises(base):
    with pytest.raises(WorkflowError, match="not found"):
        get_workflow(base, "ghost")


def test_update_workflow(base):
    create_workflow(base, "deploy", ["push"])
    entry = update_workflow(base, "deploy", ["validate", "push", "cleanup"])
    assert entry["steps"] == ["validate", "push", "cleanup"]


def test_update_missing_raises(base):
    with pytest.raises(WorkflowError, match="not found"):
        update_workflow(base, "ghost", ["step"])


def test_update_empty_steps_raises(base):
    create_workflow(base, "deploy", ["push"])
    with pytest.raises(WorkflowError, match="at least one step"):
        update_workflow(base, "deploy", [])


def test_delete_workflow(base):
    create_workflow(base, "deploy", ["push"])
    delete_workflow(base, "deploy")
    with pytest.raises(WorkflowError):
        get_workflow(base, "deploy")


def test_delete_missing_raises(base):
    with pytest.raises(WorkflowError, match="not found"):
        delete_workflow(base, "ghost")


def test_list_empty(base):
    assert list_workflows(base) == []


def test_list_returns_all(base):
    create_workflow(base, "a", ["step1"])
    create_workflow(base, "b", ["step2", "step3"])
    names = [e["name"] for e in list_workflows(base)]
    assert set(names) == {"a", "b"}
