"""Profile management: named collections of environment variable overrides."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from envoy_cli.storage import get_env_dir


class ProfileError(Exception):
    pass


def get_profile_dir(base_dir: Optional[Path] = None) -> Path:
    root = base_dir or get_env_dir()
    return root / "profiles"


def profile_path(profile_name: str, base_dir: Optional[Path] = None) -> Path:
    return get_profile_dir(base_dir) / f"{profile_name}.json"


def save_profile(profile_name: str, overrides: Dict[str, str], base_dir: Optional[Path] = None) -> Path:
    """Persist a named profile of key/value overrides."""
    if not profile_name.strip():
        raise ProfileError("Profile name must not be empty.")
    path = profile_path(profile_name, base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(overrides, indent=2), encoding="utf-8")
    return path


def load_profile(profile_name: str, base_dir: Optional[Path] = None) -> Dict[str, str]:
    """Load a named profile; raises ProfileError if not found."""
    path = profile_path(profile_name, base_dir)
    if not path.exists():
        raise ProfileError(f"Profile '{profile_name}' not found.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ProfileError(f"Profile '{profile_name}' is malformed.")
    return data


def list_profiles(base_dir: Optional[Path] = None) -> List[str]:
    """Return sorted list of profile names."""
    d = get_profile_dir(base_dir)
    if not d.exists():
        return []
    return sorted(p.stem for p in d.glob("*.json"))


def delete_profile(profile_name: str, base_dir: Optional[Path] = None) -> None:
    """Delete a named profile; raises ProfileError if not found."""
    path = profile_path(profile_name, base_dir)
    if not path.exists():
        raise ProfileError(f"Profile '{profile_name}' not found.")
    path.unlink()


def apply_profile(env_vars: Dict[str, str], profile_name: str, base_dir: Optional[Path] = None) -> Dict[str, str]:
    """Return a new dict with profile overrides merged on top of env_vars."""
    overrides = load_profile(profile_name, base_dir)
    merged = dict(env_vars)
    merged.update(overrides)
    return merged
