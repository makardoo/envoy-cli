"""Compare two stored env environments side by side."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from envoy_cli.storage import load_env
from envoy_cli.env_file import decrypt_env, parse_env


@dataclass
class CompareResult:
    only_in_a: List[str]
    only_in_b: List[str]
    different_values: List[str]
    same_keys: List[str]


class CompareError(Exception):
    pass


def _decrypt_to_dict(env_name: str, passphrase: str, base_dir: Optional[str] = None) -> Dict[str, str]:
    kwargs = {"base_dir": base_dir} if base_dir else {}
    raw = load_env(env_name, **kwargs)
    decrypted = decrypt_env(raw, passphrase)
    pairs = parse_env(decrypted)
    return dict(pairs)


def compare_envs(
    env_a: str,
    env_b: str,
    passphrase_a: str,
    passphrase_b: Optional[str] = None,
    base_dir: Optional[str] = None,
) -> CompareResult:
    """Compare two stored envs. Uses passphrase_a for both if passphrase_b is omitted."""
    if passphrase_b is None:
        passphrase_b = passphrase_a

    try:
        dict_a = _decrypt_to_dict(env_a, passphrase_a, base_dir)
    except Exception as exc:
        raise CompareError(f"Could not load '{env_a}': {exc}") from exc

    try:
        dict_b = _decrypt_to_dict(env_b, passphrase_b, base_dir)
    except Exception as exc:
        raise CompareError(f"Could not load '{env_b}': {exc}") from exc

    keys_a = set(dict_a)
    keys_b = set(dict_b)

    only_in_a = sorted(keys_a - keys_b)
    only_in_b = sorted(keys_b - keys_a)
    common = keys_a & keys_b
    different_values = sorted(k for k in common if dict_a[k] != dict_b[k])
    same_keys = sorted(k for k in common if dict_a[k] == dict_b[k])

    return CompareResult(
        only_in_a=only_in_a,
        only_in_b=only_in_b,
        different_values=different_values,
        same_keys=same_keys,
    )


def format_compare(result: CompareResult, env_a: str, env_b: str, show_same: bool = False) -> str:
    lines: List[str] = []
    for key in result.only_in_a:
        lines.append(f"< {key}  (only in {env_a})")
    for key in result.only_in_b:
        lines.append(f"> {key}  (only in {env_b})")
    for key in result.different_values:
        lines.append(f"~ {key}  (value differs)")
    if show_same:
        for key in result.same_keys:
            lines.append(f"= {key}")
    return "\n".join(lines) if lines else "(no differences)"
