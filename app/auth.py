"""Authentication helpers."""

from __future__ import annotations

import hashlib


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(stored_hash: str, presented: str) -> bool:
    return stored_hash == hash_password(presented)
