"""Tests for envoy_cli.crypto encryption/decryption utilities."""

import pytest
from envoy_cli.crypto import encrypt, decrypt


PASSPHRASE = "super-secret-passphrase-123"


def test_encrypt_returns_string():
    token = encrypt("hello", PASSPHRASE)
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_decrypt_roundtrip():
    original = "my_secret_value"
    token = encrypt(original, PASSPHRASE)
    recovered = decrypt(token, PASSPHRASE)
    assert recovered == original


def test_encrypt_produces_different_ciphertext_each_time():
    value = "same_value"
    token1 = encrypt(value, PASSPHRASE)
    token2 = encrypt(value, PASSPHRASE)
    assert token1 != token2  # different nonce/salt each time


def test_decrypt_wrong_passphrase_raises():
    token = encrypt("secret", PASSPHRASE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-passphrase")


def test_decrypt_invalid_payload_raises():
    with pytest.raises(ValueError):
        decrypt("not-valid-base64!!!", PASSPHRASE)


def test_decrypt_short_payload_raises():
    import base64
    short = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short, PASSPHRASE)


def test_encrypt_empty_string():
    token = encrypt("", PASSPHRASE)
    recovered = decrypt(token, PASSPHRASE)
    assert recovered == ""


def test_encrypt_unicode_value():
    value = "pässwörд_🔑"
    token = encrypt(value, PASSPHRASE)
    assert decrypt(token, PASSPHRASE) == value
