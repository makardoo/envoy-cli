"""Sync module for pushing and pulling .env files to/from remote profiles."""

import os
import json
from pathlib import Path
from typing import Optional

from envoy_cli.storage import save_env, load_env, env_file_path, list_envs
from envoy_cli.env_file import encrypt_env, decrypt_env, parse_env, serialize_env

REMOTE_INDEX_FILENAME = ".envoy_index.json"


def get_remote_index(remote_dir: str) -> dict:
    """Load the remote index file mapping env names to metadata."""
    index_path = Path(remote_dir) / REMOTE_INDEX_FILENAME
    if not index_path.exists():
        return {}
    with open(index_path, "r") as f:
        return json.load(f)


def save_remote_index(remote_dir: str, index: dict) -> None:
    """Persist the remote index file."""
    index_path = Path(remote_dir) / REMOTE_INDEX_FILENAME
    Path(remote_dir).mkdir(parents=True, exist_ok=True)
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


def push_env(name: str, passphrase: str, remote_dir: str, store_dir: Optional[str] = None) -> str:
    """Encrypt and push a local env file to the remote directory.

    Returns the remote file path.
    """
    raw_content = load_env(name, store_dir=store_dir)
    env_vars = parse_env(raw_content)
    encrypted_content = encrypt_env(env_vars, passphrase)
    serialized = serialize_env(encrypted_content)

    remote_path = Path(remote_dir) / f"{name}.env"
    Path(remote_dir).mkdir(parents=True, exist_ok=True)
    remote_path.write_text(serialized)

    index = get_remote_index(remote_dir)
    index[name] = {"file": f"{name}.env", "encrypted": True}
    save_remote_index(remote_dir, index)

    return str(remote_path)


def pull_env(name: str, passphrase: str, remote_dir: str, store_dir: Optional[str] = None) -> str:
    """Pull and decrypt a remote env file into local storage.

    Returns the local file path.
    """
    index = get_remote_index(remote_dir)
    if name not in index:
        raise KeyError(f"Remote env '{name}' is not listed in the remote index.")

    remote_path = Path(remote_dir) / f"{name}.env"
    if not remote_path.exists():
        raise FileNotFoundError(f"Remote env '{name}' not found at {remote_path}")

    serialized = remote_path.read_text()
    encrypted_vars = parse_env(serialized)
    decrypted_vars = decrypt_env(encrypted_vars, passphrase)
    plain_content = serialize_env(decrypted_vars)

    local_path = save_env(name, plain_content, store_dir=store_dir)
    return str(local_path)


def list_remote_envs(remote_dir: str) -> list:
    """Return a list of env names available in the remote directory."""
    index = get_remote_index(remote_dir)
    return list(index.keys())
