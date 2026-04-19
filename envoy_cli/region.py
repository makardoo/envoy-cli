"""Region assignment for env files."""
import json
from pathlib import Path

VALID_REGIONS = {"us-east", "us-west", "eu-west", "ap-south", "local"}


class RegionError(Exception):
    pass


def _regions_path(base_dir: str) -> Path:
    return Path(base_dir) / "regions.json"


def _load(base_dir: str) -> dict:
    p = _regions_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save(base_dir: str, data: dict) -> None:
    p = _regions_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


def set_region(base_dir: str, env_name: str, region: str) -> None:
    if not env_name:
        raise RegionError("env_name must not be empty")
    if region not in VALID_REGIONS:
        raise RegionError(f"Invalid region '{region}'. Valid: {sorted(VALID_REGIONS)}")
    data = _load(base_dir)
    data[env_name] = region
    _save(base_dir, data)


def get_region(base_dir: str, env_name: str) -> str:
    if not env_name:
        raise RegionError("env_name must not be empty")
    data = _load(base_dir)
    if env_name not in data:
        raise RegionError(f"No region assigned for '{env_name}'")
    return data[env_name]


def remove_region(base_dir: str, env_name: str) -> None:
    data = _load(base_dir)
    if env_name not in data:
        raise RegionError(f"No region assigned for '{env_name}'")
    del data[env_name]
    _save(base_dir, data)


def list_regions(base_dir: str) -> dict:
    return _load(base_dir)
