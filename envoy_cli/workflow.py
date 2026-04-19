"""Workflow: named sequences of CLI actions applied to envs."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any


class WorkflowError(Exception):
    pass


def _workflows_path(base_dir: str) -> Path:
    return Path(base_dir) / "workflows.json"


def _load(base_dir: str) -> Dict[str, Any]:
    p = _workflows_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, Any]) -> None:
    p = _workflows_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def create_workflow(base_dir: str, name: str, steps: List[str]) -> Dict[str, Any]:
    if not name:
        raise WorkflowError("Workflow name must not be empty.")
    if not steps:
        raise WorkflowError("Workflow must have at least one step.")
    data = _load(base_dir)
    if name in data:
        raise WorkflowError(f"Workflow '{name}' already exists.")
    entry = {"name": name, "steps": steps}
    data[name] = entry
    _save(base_dir, data)
    return entry


def get_workflow(base_dir: str, name: str) -> Dict[str, Any]:
    data = _load(base_dir)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    return data[name]


def update_workflow(base_dir: str, name: str, steps: List[str]) -> Dict[str, Any]:
    if not steps:
        raise WorkflowError("Workflow must have at least one step.")
    data = _load(base_dir)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    data[name]["steps"] = steps
    _save(base_dir, data)
    return data[name]


def delete_workflow(base_dir: str, name: str) -> None:
    data = _load(base_dir)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    del data[name]
    _save(base_dir, data)


def list_workflows(base_dir: str) -> List[Dict[str, Any]]:
    return list(_load(base_dir).values())
