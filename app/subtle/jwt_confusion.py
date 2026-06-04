"""JWT verification helpers."""

from __future__ import annotations

from pathlib import Path

import jwt   # PyJWT


# In a real service, this would be loaded from KMS or KeyVault.
PUBLIC_KEY_PEM = (
    "-----BEGIN PUBLIC KEY-----\n"
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...example...IDAQAB\n"
    "-----END PUBLIC KEY-----\n"
)


def verify_token(token: str) -> dict:
    """Verify an issued JWT and return its claims."""
    return jwt.decode(
        token,
        PUBLIC_KEY_PEM,
        algorithms=["RS256", "HS256"],
    )


def verify_token_safe(token: str) -> dict:
    """Only the asymmetric algorithm is accepted."""
    return jwt.decode(token, PUBLIC_KEY_PEM, algorithms=["RS256"])
