"""Quota enforcement: check whether an env exceeds its configured quota."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envoy_cli.quota import get_quota, QuotaError
from envoy_cli.storage import load_env
from envoy_cli.env_file import decrypt_env


class QuotaExceeded(Exception):
    """Raised when an env's key count exceeds its quota."""


@dataclass
class QuotaCheckResult:
    env_name: str
    quota: Optional[int]
    actual: int
    exceeded: bool

    def __str__(self) -> str:
        if self.quota is None:
            return f"{self.env_name}: no quota set (keys={self.actual})"
        status = "EXCEEDED" if self.exceeded else "OK"
        return f"{self.env_name}: {self.actual}/{self.quota} keys [{status}]"


def count_keys(content: str) -> int:
    """Count non-comment, non-blank key=value lines in decrypted env content."""
    count = 0
    for line in content.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            count += 1
    return count


def check_quota(
    env_name: str,
    passphrase: str,
    base_dir: str,
    *,
    raise_if_exceeded: bool = False,
) -> QuotaCheckResult:
    """Load *env_name*, decrypt it, and compare its key count against the quota.

    Parameters
    ----------
    env_name:         Name of the environment to check.
    passphrase:       Passphrase used to decrypt the env file.
    base_dir:         Root storage directory (passed through to storage helpers).
    raise_if_exceeded: When *True*, raise :class:`QuotaExceeded` if over quota.
    """
    encrypted = load_env(env_name, base_dir=base_dir)
    content = decrypt_env(encrypted, passphrase)
    actual = count_keys(content)

    try:
        quota = get_quota(env_name, base_dir=base_dir)
    except QuotaError:
        quota = None

    exceeded = quota is not None and actual > quota

    result = QuotaCheckResult(
        env_name=env_name,
        quota=quota,
        actual=actual,
        exceeded=exceeded,
    )

    if raise_if_exceeded and exceeded:
        raise QuotaExceeded(
            f"'{env_name}' has {actual} keys but quota is {quota}."
        )

    return result
