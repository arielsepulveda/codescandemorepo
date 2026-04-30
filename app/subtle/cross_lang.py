"""Cross-language type confusion: Python emits "false", JS interprets it.

THE BUG
-------
The Python backend sets a flag in JSON serialization the wrong way. The
JavaScript frontend reads it with truthy semantics. Result: a flag named
``is_admin`` whose backend value is ``"false"`` (string) is interpreted by
the frontend as ``true`` (truthy non-empty string).

This is **half** of the bug. The other half is in ``cross_lang.js`` —
neither file alone shows the vulnerability.

THE EXPLOIT
-----------
Any user who hits the dashboard sees admin features.

WHY SAST MISSES IT
------------------
- CodeQL scans Python and JS in separate analyses. Even multi-language
  projects don't get cross-language taint flow today.
- The Python file alone looks fine — JSON serialization is structurally
  legal.
- The JS file alone looks fine — the truthiness check is idiomatic JS.
- The bug is in the *contract* between the two languages.

A reasoning auditor can see both files in the same scan, notice the API
boundary, recognize the ``"false"`` string vs JS truthy semantics, and
flag it.

THE FIX
-------
Don't stringify booleans. Or use a typed contract (Pydantic + TypeScript
generated from it; OpenAPI; gRPC).
"""

from __future__ import annotations

import json
from flask import Blueprint, jsonify, request

bp = Blueprint("cross_lang", __name__)


@bp.route("/api/me")
def get_me():
    user_id = request.args.get("user_id")
    is_admin = _check_admin(user_id)
    # ❌ Stringifying the boolean. The frontend's `if (data.is_admin)`
    # check sees "false" — a non-empty string — as truthy.
    return jsonify({
        "id": user_id,
        "name": "Alice",
        "is_admin": str(is_admin).lower(),    # "true" or "false" — both truthy in JS
    })


def _check_admin(user_id: str | None) -> bool:
    return user_id == "1"   # toy implementation
