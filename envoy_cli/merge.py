"""Merge two env environments with conflict resolution strategies."""
from __future__ import annotations
from enum import Enum
from typing import Dict, List, NamedTuple

from envoy_cli.storage import load_env
from envoy_cli.env_file import decrypt_env, parse_env


class MergeStrategy(str, Enum):
    OURS = "ours"       # keep value from base env on conflict
    THEIRS = "theirs"   # keep value from other env on conflict
    UNION = "union"     # keep all keys; base wins on conflict (same as OURS)


class MergeConflict(NamedTuple):
    key: str
    base_value: str
    other_value: str


class MergeResult(NamedTuple):
    merged: Dict[str, str]
    conflicts: List[MergeConflict]


class MergeError(Exception):
    pass


def merge_dicts(
    base: Dict[str, str],
    other: Dict[str, str],
    strategy: MergeStrategy = MergeStrategy.OURS,
) -> MergeResult:
    """Merge two env dicts according to the given strategy."""
    merged: Dict[str, str] = dict(base)
    conflicts: List[MergeConflict] = []

    for key, other_val in other.items():
        if key not in merged:
            merged[key] = other_val
        elif merged[key] != other_val:
            conflict = MergeConflict(key, merged[key], other_val)
            conflicts.append(conflict)
            if strategy == MergeStrategy.THEIRS:
                merged[key] = other_val
            # OURS / UNION: keep base value (already set)

    return MergeResult(merged=merged, conflicts=conflicts)


def merge_envs(
    base_name: str,
    other_name: str,
    passphrase: str,
    strategy: MergeStrategy = MergeStrategy.OURS,
    base_dir: str | None = None,
) -> MergeResult:
    """Load two stored envs, decrypt, and merge them."""
    try:
        base_raw = load_env(base_name, base_dir=base_dir)
    except FileNotFoundError:
        raise MergeError(f"Env '{base_name}' not found.")
    try:
        other_raw = load_env(other_name, base_dir=base_dir)
    except FileNotFoundError:
        raise MergeError(f"Env '{other_name}' not found.")

    base_plain = decrypt_env(base_raw, passphrase)
    other_plain = decrypt_env(other_raw, passphrase)

    base_dict = dict(parse_env(base_plain))
    other_dict = dict(parse_env(other_plain))

    return merge_dicts(base_dict, other_dict, strategy)
