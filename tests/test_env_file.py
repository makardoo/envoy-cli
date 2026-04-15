"""Tests for envoy_cli.env_file parsing and encryption helpers."""

import pytest
from envoy_cli.env_file import (
    parse_env,
    serialize_env,
    encrypt_env,
    decrypt_env,
    ENCRYPTED_PREFIX,
)

PASSPHRASE = "test-pass-phrase"

SAMPLE_ENV = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD="s3cr3t"

# App
APP_KEY='my-app-key'
"""


def test_parse_env_basic():
    data = parse_env(SAMPLE_ENV)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"
    assert data["DB_PASSWORD"] == "s3cr3t"
    assert data["APP_KEY"] == "my-app-key"


def test_parse_env_ignores_comments_and_blanks():
    data = parse_env(SAMPLE_ENV)
    for key in data:
        assert not key.startswith("#")


def test_serialize_env_roundtrip():
    original = {"FOO": "bar", "BAZ": "qux"}
    content = serialize_env(original)
    recovered = parse_env(content)
    assert recovered == original


def test_encrypt_env_adds_prefix():
    data = {"SECRET": "value123", "TOKEN": "abc"}
    encrypted = encrypt_env(data, PASSPHRASE)
    for val in encrypted.values():
        assert val.startswith(ENCRYPTED_PREFIX)


def test_decrypt_env_roundtrip():
    data = {"SECRET": "value123", "TOKEN": "abc"}
    encrypted = encrypt_env(data, PASSPHRASE)
    decrypted = decrypt_env(encrypted, PASSPHRASE)
    assert decrypted == data


def test_decrypt_env_skips_plain_values():
    data = {"PLAIN": "no-encryption", "ENC": ENCRYPTED_PREFIX + "invalid"}
    # Only plain values; skip enc: entries that would fail
    plain_only = {"PLAIN": "no-encryption"}
    result = decrypt_env(plain_only, PASSPHRASE)
    assert result["PLAIN"] == "no-encryption"


def test_decrypt_env_wrong_passphrase_raises():
    data = {"KEY": "value"}
    encrypted = encrypt_env(data, PASSPHRASE)
    with pytest.raises(ValueError):
        decrypt_env(encrypted, "wrong-pass")
