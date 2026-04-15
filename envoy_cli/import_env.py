"""Import .env files from various sources into envoy-cli storage."""

import os
import re
from pathlib import Path
from typing import Optional


SUPPORTED_FORMATS = ["dotenv", "docker", "shell"]


def detect_format(content: str) -> str:
    """Attempt to detect the format of an env file."""
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    for line in lines:
        if line.startswith("export "):
            return "shell"
    return "dotenv"


def parse_dotenv(content: str) -> dict:
    """Parse a standard .env file into a dict."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Strip 'export ' prefix if present
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def parse_docker_env(content: str) -> dict:
    """Parse a Docker-style env file (key=value, no quotes required)."""
    return parse_dotenv(content)


def import_from_file(filepath: str, fmt: Optional[str] = None) -> dict:
    """Read an env file from disk and return parsed key/value pairs."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    content = path.read_text(encoding="utf-8")
    if fmt is None:
        fmt = detect_format(content)
    if fmt in ("dotenv", "shell", "docker"):
        return parse_dotenv(content)
    raise ValueError(f"Unsupported format: {fmt}. Choose from {SUPPORTED_FORMATS}")


def import_from_string(content: str, fmt: Optional[str] = None) -> dict:
    """Parse env content from a raw string."""
    if fmt is None:
        fmt = detect_format(content)
    if fmt in ("dotenv", "shell", "docker"):
        return parse_dotenv(content)
    raise ValueError(f"Unsupported format: {fmt}. Choose from {SUPPORTED_FORMATS}")


def merge_envs(base: dict, override: dict, strategy: str = "override") -> dict:
    """Merge two env dicts. strategy='override' replaces existing keys."""
    if strategy == "override":
        merged = dict(base)
        merged.update(override)
        return merged
    elif strategy == "keep":
        merged = dict(override)
        merged.update(base)
        return merged
    raise ValueError(f"Unknown merge strategy: {strategy}")
