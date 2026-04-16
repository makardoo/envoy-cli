"""Search across stored env files for keys or values."""
from __future__ import annotations
from typing import List, Tuple
from envoy_cli.storage import list_envs, load_env
from envoy_cli.env_file import decrypt_env, parse_env


class SearchError(Exception):
    pass


def search_key(
    base_dir: str, passphrase: str, pattern: str, env_name: str | None = None
) -> List[Tuple[str, str, str]]:
    """Return [(env_name, key, value)] where key contains pattern."""
    results = []
    names = [env_name] if env_name else list_envs(base_dir)
    for name in names:
        try:
            raw = load_env(base_dir, name)
            decrypted = decrypt_env(raw, passphrase)
            pairs = parse_env(decrypted)
        except Exception:
            continue
        for k, v in pairs:
            if pattern.lower() in k.lower():
                results.append((name, k, v))
    return results


def search_value(
    base_dir: str, passphrase: str, pattern: str, env_name: str | None = None
) -> List[Tuple[str, str, str]]:
    """Return [(env_name, key, value)] where value contains pattern."""
    results = []
    names = [env_name] if env_name else list_envs(base_dir)
    for name in names:
        try:
            raw = load_env(base_dir, name)
            decrypted = decrypt_env(raw, passphrase)
            pairs = parse_env(decrypted)
        except Exception:
            continue
        for k, v in pairs:
            if pattern.lower() in v.lower():
                results.append((name, k, v))
    return results
