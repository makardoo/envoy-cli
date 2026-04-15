"""Key rotation: re-encrypt stored env files with a new passphrase."""

from typing import List, Tuple
from envoy_cli.storage import list_envs, load_env, save_env
from envoy_cli.env_file import decrypt_env, encrypt_env


class RotationError(Exception):
    """Raised when rotation fails for one or more environments."""


def rotate_single(
    env_name: str,
    old_passphrase: str,
    new_passphrase: str,
    store_dir: str | None = None,
) -> None:
    """Re-encrypt a single env file with a new passphrase.

    Args:
        env_name: Name of the environment (e.g. "production").
        old_passphrase: Current passphrase used to decrypt.
        new_passphrase: New passphrase to encrypt with.
        store_dir: Optional custom store directory.

    Raises:
        FileNotFoundError: If the env file does not exist.
        ValueError: If decryption with the old passphrase fails.
    """
    kwargs = {"store_dir": store_dir} if store_dir else {}
    encrypted_content = load_env(env_name, **kwargs)
    plaintext = decrypt_env(encrypted_content, old_passphrase)
    re_encrypted = encrypt_env(plaintext, new_passphrase)
    save_env(env_name, re_encrypted, **kwargs)


def rotate_all(
    old_passphrase: str,
    new_passphrase: str,
    store_dir: str | None = None,
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """Re-encrypt all stored env files with a new passphrase.

    Returns:
        A tuple of (succeeded_names, failed_pairs) where failed_pairs is a
        list of (env_name, error_message) tuples.
    """
    kwargs = {"store_dir": store_dir} if store_dir else {}
    names = list_envs(**kwargs)
    succeeded: List[str] = []
    failed: List[Tuple[str, str]] = []

    for name in names:
        try:
            rotate_single(name, old_passphrase, new_passphrase, store_dir=store_dir)
            succeeded.append(name)
        except Exception as exc:  # noqa: BLE001
            failed.append((name, str(exc)))

    return succeeded, failed
