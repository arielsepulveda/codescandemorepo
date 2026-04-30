"""JWT algorithm confusion (RS256 ↔ HS256) — a real CVE-class.

THE BUG
-------
The service issues tokens signed RS256 (asymmetric, with a published public
key). When verifying, it passes a list ``algorithms=["RS256", "HS256"]``
without checking which one the *incoming* token actually uses, AND it
hands the *public* key to the verifier as the secret.

This is the textbook JWT alg-confusion attack:

  1. Take a legitimate RS256 token. Modify the header to ``alg: HS256``.
  2. Re-sign it with HMAC-SHA256, using the service's *public* key bytes
     as the HMAC secret (the public key is, by definition, public).
  3. The verifier accepts ``alg=HS256`` (it's in the list). For HS256 it
     uses the same key it had — the public key — as the HMAC secret.
     Your forged token verifies.

THE EXPLOIT
-----------
- Forge a token with arbitrary claims (sub, role=admin, etc.).
- The endpoint accepts it as legitimately signed by the issuer.

WHY SAST MISSES IT
------------------
- CodeQL has a query for hardcoded JWT secrets and for missing
  signature verification, but not for *algorithm confusion*. The unsafe
  call is structurally identical to the safe call:
    - Safe:   ``jwt.decode(tok, public_key, algorithms=["RS256"])``
    - Unsafe: ``jwt.decode(tok, public_key, algorithms=["RS256", "HS256"])``
- Knowing that adding HS256 to a list of allowed algs is fatal *given*
  that the same key is used for verification requires understanding the
  algorithms involved. Pattern matchers don't.
"""

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
    """Verify an issued JWT and return its claims.

    ❌ Allowing both RS256 and HS256 with the public key as the secret is
    catastrophic — see module docstring.
    """
    return jwt.decode(
        token,
        PUBLIC_KEY_PEM,
        algorithms=["RS256", "HS256"],   # bug: HS256 must not be accepted
    )


def verify_token_safe(token: str) -> dict:
    """For contrast: only the asymmetric algorithm is accepted."""
    return jwt.decode(token, PUBLIC_KEY_PEM, algorithms=["RS256"])
