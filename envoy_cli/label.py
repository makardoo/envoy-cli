"""Label management for env entries."""
from __future__ import annotations
import json
from pathlib import Path


class LabelError(Exception):
    pass


def _labels_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "labels.json"


def _load(base_dir: str) -> dict:
    p = _labels_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _labels_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_label(base_dir: str, env_name: str, label: str) -> None:
    if not env_name:
        raise LabelError("env_name must not be empty")
    if not label:
        raise LabelError("label must not be empty")
    data = _load(base_dir)
    labels = data.get(env_name, [])
    if label not in labels:
        labels.append(label)
    data[env_name] = labels
    _save(base_dir, data)


def remove_label(base_dir: str, env_name: str, label: str) -> None:
    data = _load(base_dir)
    labels = data.get(env_name, [])
    if label not in labels:
        raise LabelError(f"Label '{label}' not found on '{env_name}'")
    labels.remove(label)
    data[env_name] = labels
    _save(base_dir, data)


def get_labels(base_dir: str, env_name: str) -> list[str]:
    return _load(base_dir).get(env_name, [])


def list_all(base_dir: str) -> dict[str, list[str]]:
    return _load(base_dir)


def find_by_label(base_dir: str, label: str) -> list[str]:
    return [name for name, labels in _load(base_dir).items() if label in labels]
