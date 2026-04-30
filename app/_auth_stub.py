"""Placeholder identity / authorization helpers used by the subtle/ demos.

In a real app these come from your auth framework. The bodies are stubs;
the auditor only needs to see the API surface to reason about the call
sites in ``app/subtle/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class User:
    id: int
    role: str = "user"


def current_user() -> User:
    """Returns the authenticated user (from session). Stub."""
    return User(id=42, role="user")


def is_admin() -> bool:
    return current_user().role == "admin"


def lookup_record(record_id: int) -> dict[str, Any]:
    return {"id": record_id, "data": "..."}
