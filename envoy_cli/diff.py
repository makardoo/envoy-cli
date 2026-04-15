"""Diff utilities for comparing .env file versions."""

from typing import Dict, List, Tuple


def parse_env_dict(content: str) -> Dict[str, str]:
    """Parse env content into a key-value dictionary, ignoring comments and blanks."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip()
    return result


def diff_envs(
    old_content: str, new_content: str
) -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Compare two env file contents and return a structured diff.

    Returns a dict with keys:
      - 'added':   list of (key, new_value)
      - 'removed': list of (key, old_value)
      - 'changed': list of (key, old_value, new_value)
      - 'unchanged': list of (key, value)
    """
    old = parse_env_dict(old_content)
    new = parse_env_dict(new_content)

    all_keys = set(old) | set(new)

    added = []
    removed = []
    changed = []
    unchanged = []

    for key in sorted(all_keys):
        if key in new and key not in old:
            added.append((key, new[key]))
        elif key in old and key not in new:
            removed.append((key, old[key]))
        elif old[key] != new[key]:
            changed.append((key, old[key], new[key]))
        else:
            unchanged.append((key, old[key]))

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def format_diff(diff: Dict[str, list], mask_values: bool = True) -> str:
    """Format a diff dict into a human-readable string."""
    lines = []

    def mask(val: str) -> str:
        return "***" if mask_values else val

    for key, value in diff.get("added", []):
        lines.append(f"  + {key}={mask(value)}")
    for key, value in diff.get("removed", []):
        lines.append(f"  - {key}={mask(value)}")
    for key, old_val, new_val in diff.get("changed", []):
        lines.append(f"  ~ {key}: {mask(old_val)} -> {mask(new_val)}")

    if not lines:
        return "No differences found."

    summary = (
        f"+{len(diff.get('added', []))} "
        f"-{len(diff.get('removed', []))} "
        f"~{len(diff.get('changed', []))}"
    )
    return summary + "\n" + "\n".join(lines)
