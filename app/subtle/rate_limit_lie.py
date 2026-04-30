"""Spec violation: docstring promises rate limiting; code doesn't enforce it.

THE BUG
-------
A LLM auditor reads this and sees that the *intent* (per docstring + the
``@rate_limited`` decorator name) is "5 requests per minute per user". The
implementation, however, does not actually enforce anything — the decorator
decrements a counter that's reset on every request because ``_counters``
is a function-local dict.

THE EXPLOIT
-----------
- Hammer ``/api/expensive`` with 10,000 requests/sec. None are rejected.
- The ``@rate_limited`` decorator is decorative — it logs but does not
  block.

WHY SAST MISSES IT
------------------
- The bug is the *gap between the spec and the implementation*. The spec
  lives in the docstring (English text) and the decorator name (a token).
  CodeQL doesn't read English. SonarQube doesn't read decorator semantics.
- A reviewer (or LLM) who reads the docstring expects state-keeping per
  user across requests. This implementation creates a fresh ``_counters``
  on every call, so the limit is meaningless.
- Pattern matchers can flag "uses Redis correctly for rate limiting" only
  if they have a positive signature for the *correct* pattern; they cannot
  flag the *absence* of one. This is the classic "negative-space"
  vulnerability class.

This is the kind of bug that ships when a junior developer adds a
``@rate_limited`` decorator to silence an audit ticket without actually
implementing the limit.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from flask import Blueprint, request

api = Blueprint("metered_api", __name__)


def rate_limited(calls_per_minute: int) -> Callable:
    """Limits each user to ``calls_per_minute`` requests per minute.

    Resets every minute. Excess requests get HTTP 429.
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # ❌ ``_counters`` is created fresh on every request, so the
            # "limit" is per-request, not per-user-per-minute. The decorator
            # is a lie — but the docstring + name make it look correct.
            _counters: dict[str, int] = {}
            user = request.headers.get("X-User", "anon")
            _counters[user] = _counters.get(user, 0) + 1
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@api.route("/api/expensive")
@rate_limited(calls_per_minute=5)
def expensive() -> dict:
    """Expensive operation — supposedly rate-limited."""
    return {"work": "done"}
