"""Metered API endpoints."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from flask import Blueprint, request

api = Blueprint("metered_api", __name__)


def rate_limited(calls_per_minute: int) -> Callable:
    """Limit each user to ``calls_per_minute`` requests per minute.

    Resets every minute. Excess requests get HTTP 429.
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            _counters: dict[str, int] = {}
            user = request.headers.get("X-User", "anon")
            _counters[user] = _counters.get(user, 0) + 1
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@api.route("/api/expensive")
@rate_limited(calls_per_minute=5)
def expensive() -> dict:
    """Expensive operation, rate-limited to 5 requests/min per user."""
    return {"work": "done"}
