"""Tier assignment for env files (e.g. free, pro, enterprise)."""
from __future__ import annotations
import json
from pathlib import Path

VALID_TIERS = {"free", "pro", "enterprise"}


class TierError(Exception):
    pass


def _tiers_path(base_dir: str) -> Path:
    return Path(base_dir) / "tiers.json"


def _load(base_dir: str) -> dict:
    p = _tiers_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _tiers_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_tier(base_dir: str, env_name: str, tier: str) -> None:
    if not env_name:
        raise TierError("env_name must not be empty")
    if tier not in VALID_TIERS:
        raise TierError(f"Invalid tier '{tier}'. Choose from: {sorted(VALID_TIERS)}")
    data = _load(base_dir)
    data[env_name] = tier
    _save(base_dir, data)


def get_tier(base_dir: str, env_name: str) -> str:
    data = _load(base_dir)
    if env_name not in data:
        raise TierError(f"No tier set for '{env_name}'")
    return data[env_name]


def remove_tier(base_dir: str, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise TierError(f"No tier set for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_tiers(base_dir: str) -> dict[str, str]:
    return _load(base_dir)
