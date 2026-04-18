"""Group management: assign env files to named groups and list members."""
from __future__ import annotations

import json
from pathlib import Path


class GroupError(Exception):
    pass


def _groups_path(base_dir: str) -> Path:
    return Path(base_dir) / "groups.json"


def _load(base_dir: str) -> dict:
    p = _groups_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _groups_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def add_to_group(base_dir: str, group: str, env_name: str) -> None:
    if not group.strip():
        raise GroupError("Group name must not be empty.")
    if not env_name.strip():
        raise GroupError("Env name must not be empty.")
    data = _load(base_dir)
    members: list = data.setdefault(group, [])
    if env_name not in members:
        members.append(env_name)
    _save(base_dir, data)


def remove_from_group(base_dir: str, group: str, env_name: str) -> None:
    data = _load(base_dir)
    if group not in data or env_name not in data[group]:
        raise GroupError(f"'{env_name}' is not in group '{group}'.")
    data[group].remove(env_name)
    if not data[group]:
        del data[group]
    _save(base_dir, data)


def list_group(base_dir: str, group: str) -> list[str]:
    data = _load(base_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' not found.")
    return list(data[group])


def list_all_groups(base_dir: str) -> dict[str, list[str]]:
    return _load(base_dir)


def delete_group(base_dir: str, group: str) -> None:
    data = _load(base_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' not found.")
    del data[group]
    _save(base_dir, data)
