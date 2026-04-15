"""Parse, encrypt, and serialize .env files."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from envoy_cli.crypto import encrypt, decrypt

ENCRYPTED_PREFIX = "enc:"


def parse_env(content: str) -> Dict[str, str]:
    """Parse .env file content into a key-value dictionary."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def serialize_env(data: Dict[str, str]) -> str:
    """Serialize a key-value dictionary back into .env file content."""
    lines = [f"{key}={value}" for key, value in data.items()]
    return "\n".join(lines) + "\n"


def encrypt_env(data: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Return a new dict with all values encrypted."""
    return {
        key: ENCRYPTED_PREFIX + encrypt(value, passphrase)
        for key, value in data.items()
    }


def decrypt_env(data: Dict[str, str], passphrase: str) -> Dict[str, str]:
    """Return a new dict with all encrypted values decrypted."""
    result: Dict[str, str] = {}
    for key, value in data.items():
        if value.startswith(ENCRYPTED_PREFIX):
            result[key] = decrypt(value[len(ENCRYPTED_PREFIX):], passphrase)
        else:
            result[key] = value
    return result


def load_env_file(path: Path) -> Dict[str, str]:
    """Load and parse a .env file from disk."""
    return parse_env(path.read_text(encoding="utf-8"))


def save_env_file(path: Path, data: Dict[str, str]) -> None:
    """Serialize and write a .env file to disk."""
    path.write_text(serialize_env(data), encoding="utf-8")
