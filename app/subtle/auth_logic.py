"""Authorization bypass via OR-condition — invisible to pattern SAST.

THE BUG
-------
The intent (per the docstring + variable names) is "admins can read any
record; users can only read their own". The implementation OR-chains those
two checks, which lets an attacker make BOTH conditions overlap with their
own request.

THE EXPLOIT
-----------
- Authenticate as a regular user with id=42.
- POST /records/read with body `{"target_id": 42, "as_admin": false}` — fine.
- POST /records/read with body `{"target_id": 99, "as_admin": false}` — denied.
- POST /records/read with body `{"target_id": 99, "as_admin": true}` —
  the `or current_user.id == target_id` short-circuits to True for ANY
  authenticated user when target_id == current_user.id, BUT the actual
  bug is more subtle: the auth check accepts `as_admin` from the request
  body, not from the session. Setting `as_admin: true` in the body
  satisfies `is_admin_request and ...` because Python truthiness of the
  client-controlled flag wins before the user role is even read.

WHY SAST MISSES IT
------------------
- CodeQL has rules for "user input flows into SQL" or "input flows into
  command", but no rule for "request body flag flows into authorization
  decision" — that's a logic invariant only the developer's *intent* makes
  obvious.
- SonarQube / Snyk Code: the OR-expression is syntactically valid Python
  with all variables defined. There's no "tainted sink" because there's
  no sink — just a boolean that gets returned.
- Pattern matchers can't distinguish `if user.is_admin or user.id == x`
  from `if user.is_admin and user.id == x`. Both compile, both run.
"""

from __future__ import annotations

from flask import Blueprint, abort, jsonify, request

from .._auth_stub import current_user, lookup_record    # session helpers

records = Blueprint("records", __name__)


@records.route("/records/read", methods=["POST"])
def read_record():
    """Read a record. Admins: any record. Users: only their own."""
    body = request.get_json() or {}
    target_id: int = body["target_id"]
    # ❌ The bug: `as_admin` is read from the *request body*, not the user
    # session. Anyone can pass `as_admin: true` and the first branch of
    # the OR short-circuits without consulting current_user.role.
    is_admin_request: bool = body.get("as_admin", False)

    if is_admin_request or current_user().id == target_id:
        return jsonify(lookup_record(target_id))
    abort(403)
