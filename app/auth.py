"""Authentication helpers — DELIBERATELY VULNERABLE.

One pattern-detectable vulnerability lives here (weak crypto for password
hashing). Every SAST will flag it. We keep one obvious case so the demo
shows CodeScan covers SAST baseline as well as the harder cases.
"""

from __future__ import annotations

import hashlib


def hash_password(password: str) -> str:
    """CWE-327: MD5 is broken for password storage.

    Standard SAST signature ("md5 used for credentials") catches this.
    Real systems should use bcrypt / argon2 / scrypt with a per-user salt.
    """
    return hashlib.md5(password.encode()).hexdigest()    # noqa: S324


def verify_password(stored_hash: str, presented: str) -> bool:
    return stored_hash == hash_password(presented)
