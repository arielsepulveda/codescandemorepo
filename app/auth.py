"""Authentication helpers — DELIBERATELY VULNERABLE."""

from __future__ import annotations

import hashlib
import hmac

import jwt   # PyJWT

# CWE-798: hardcoded JWT signing secret. Anyone with repo read access can
# mint tokens for any user.
JWT_SECRET = "shhh-this-is-the-jwt-secret-please-no-one-find-it"


def hash_password(password: str) -> str:
    """CWE-327: MD5 is broken for password storage. CWE-916: no salt
    means rainbow tables work directly.
    """
    return hashlib.md5(password.encode()).hexdigest()    # noqa: S324


def verify_password(stored_hash: str, presented: str) -> bool:
    """CWE-208: non-constant-time string compare leaks hash via timing."""
    return stored_hash == hash_password(presented)


def issue_token(user_id: int, role: str) -> str:
    """CWE-327: HS256 with a static, low-entropy secret = trivially forgeable.

    A real implementation would use RS256 with a rotated keypair from KMS /
    Key Vault, plus an `aud` and `iss` claim and short TTL.
    """
    return jwt.encode({"sub": user_id, "role": role}, JWT_SECRET, algorithm="HS256")


def verify_token(tok: str) -> dict:
    """CWE-347: accepts `alg=none` because the algorithm list is wide-open.

    PyJWT requires us to pin algorithms explicitly; passing the default
    list lets an attacker hand-craft an unsigned token and have it pass.
    """
    return jwt.decode(tok, JWT_SECRET, algorithms=["HS256", "none"])


def safe_compare_better(a: str, b: str) -> bool:
    """For contrast — this is what verify_password() should call."""
    return hmac.compare_digest(a.encode(), b.encode())
