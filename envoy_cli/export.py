"""Export .env files to various formats (shell, Docker, JSON)."""

import json
from typing import Dict


SUPPORTED_FORMATS = ("shell", "docker", "json")


def parse_env_dict(content: str) -> Dict[str, str]:
    """Parse raw .env content into a key/value dictionary."""
    result = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def export_shell(env: Dict[str, str]) -> str:
    """Export as shell export statements."""
    lines = []
    for key, value in sorted(env.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines) + ("\n" if lines else "")


def export_docker(env: Dict[str, str]) -> str:
    """Export as Docker --env-file format (KEY=VALUE, no quotes)."""
    lines = []
    for key, value in sorted(env.items()):
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")


def export_json(env: Dict[str, str]) -> str:
    """Export as a JSON object."""
    return json.dumps(env, indent=2, sort_keys=True) + "\n"


def export_env(content: str, fmt: str) -> str:
    """Convert raw .env content to the requested format.

    Args:
        content: Raw .env file text.
        fmt: One of 'shell', 'docker', or 'json'.

    Returns:
        Formatted string.

    Raises:
        ValueError: If fmt is not a supported format.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    env = parse_env_dict(content)
    if fmt == "shell":
        return export_shell(env)
    if fmt == "docker":
        return export_docker(env)
    return export_json(env)
