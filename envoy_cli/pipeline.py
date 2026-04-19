"""Pipeline: chain multiple env operations in sequence."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any

PIPELINE_VERSION = 1


class PipelineError(Exception):
    pass


def _pipelines_path(base_dir: str) -> Path:
    return Path(base_dir) / "pipelines.json"


def _load(base_dir: str) -> Dict[str, Any]:
    p = _pipelines_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: Dict[str, Any]) -> None:
    p = _pipelines_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def create_pipeline(base_dir: str, name: str, steps: List[str]) -> None:
    """Create a named pipeline with an ordered list of step names."""
    if not name:
        raise PipelineError("Pipeline name must not be empty.")
    if not steps:
        raise PipelineError("Pipeline must have at least one step.")
    data = _load(base_dir)
    if name in data:
        raise PipelineError(f"Pipeline '{name}' already exists.")
    data[name] = {"steps": steps, "version": PIPELINE_VERSION}
    _save(base_dir, data)


def get_pipeline(base_dir: str, name: str) -> List[str]:
    data = _load(base_dir)
    if name not in data:
        raise PipelineError(f"Pipeline '{name}' not found.")
    return data[name]["steps"]


def delete_pipeline(base_dir: str, name: str) -> None:
    data = _load(base_dir)
    if name not in data:
        raise PipelineError(f"Pipeline '{name}' not found.")
    del data[name]
    _save(base_dir, data)


def list_pipelines(base_dir: str) -> List[str]:
    return list(_load(base_dir).keys())


def update_pipeline(base_dir: str, name: str, steps: List[str]) -> None:
    if not steps:
        raise PipelineError("Pipeline must have at least one step.")
    data = _load(base_dir)
    if name not in data:
        raise PipelineError(f"Pipeline '{name}' not found.")
    data[name]["steps"] = steps
    _save(base_dir, data)
