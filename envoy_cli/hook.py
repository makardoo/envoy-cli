"""Pre/post hooks for envoy-cli lifecycle events."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

HOOK_EVENTS = ("pre-set", "post-set", "pre-get", "post-get", "pre-push", "post-push", "pre-pull", "post-pull")


class HookError(Exception):
    pass


def _hooks_path(base_dir: str) -> Path:
    return Path(base_dir) / "hooks.json"


def _load_hooks(base_dir: str) -> Dict[str, List[str]]:
    p = _hooks_path(base_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_hooks(base_dir: str, hooks: Dict[str, List[str]]) -> None:
    p = _hooks_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(hooks, f, indent=2)


def register_hook(base_dir: str, event: str, command: str) -> None:
    if event not in HOOK_EVENTS:
        raise HookError(f"Unknown event '{event}'. Valid events: {HOOK_EVENTS}")
    hooks = _load_hooks(base_dir)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    _save_hooks(base_dir, hooks)


def unregister_hook(base_dir: str, event: str, command: str) -> None:
    hooks = _load_hooks(base_dir)
    if event not in hooks or command not in hooks[event]:
        raise HookError(f"Hook '{command}' not registered for event '{event}'.")
    hooks[event].remove(command)
    if not hooks[event]:
        del hooks[event]
    _save_hooks(base_dir, hooks)


def list_hooks(base_dir: str, event: Optional[str] = None) -> Dict[str, List[str]]:
    hooks = _load_hooks(base_dir)
    if event:
        return {event: hooks.get(event, [])}
    return hooks


def run_hooks(base_dir: str, event: str, env: Optional[Dict[str, str]] = None) -> None:
    hooks = _load_hooks(base_dir)
    commands = hooks.get(event, [])
    merged_env = {**os.environ, **(env or {})}
    for cmd in commands:
        result = subprocess.run(cmd, shell=True, env=merged_env)
        if result.returncode != 0:
            raise HookError(f"Hook command failed (exit {result.returncode}): {cmd}")
