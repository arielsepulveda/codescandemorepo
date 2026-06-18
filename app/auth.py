"""Authentication helpers."""

from __future__ import annotations

import hashlib
import os

_PBKDF2_ITERATIONS = 600_000
_HASH_ALGORITHM = "sha256"


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        _HASH_ALGORITHM, password.encode(), salt, _PBKDF2_ITERATIONS
    )
    return f"{salt.hex()}${hash_bytes.hex()}"


def verify_password(stored_hash: str, presented: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        computed = hashlib.pbkdf2_hmac(
            _HASH_ALGORITHM, presented.encode(), salt, _PBKDF2_ITERATIONS
        )
        return hashlib.compare_digest(computed.hex(), hash_hex)
    except (ValueError, AttributeError):
        return False
