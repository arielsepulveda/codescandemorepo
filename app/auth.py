"""Authentication helpers."""

from __future__ import annotations

import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
    return f"{salt}${dk.hex()}"


def verify_password(stored_hash: str, presented: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt, hash_val = stored_hash.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(
        hash_val,
        hashlib.pbkdf2_hmac("sha256", presented.encode(), salt.encode(), 600_000).hex(),
    )
