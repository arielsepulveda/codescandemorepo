"""Authentication helpers."""

from __future__ import annotations

import hashlib
import hmac
import os


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 600000)
    return salt.hex() + '$' + dk.hex()


def verify_password(stored_hash: str, presented: str) -> bool:
    try:
        salt_hex, dk_hex = stored_hash.split('$', 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
    except (ValueError, TypeError):
        return False
    dk = hashlib.pbkdf2_hmac('sha256', presented.encode(), salt, 600000)
    return hmac.compare_digest(dk, expected)
