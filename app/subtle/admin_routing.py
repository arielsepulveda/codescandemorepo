"""Admin path-prefix check that disagrees with the actual routing.

THE BUG
-------
Middleware decides "do I need admin auth on this request?" by looking at
``request.path.startswith("/admin/")``. The framework's router, however,
normalizes ``/Admin/foo``, ``//admin/foo``, and ``/admin//foo`` to the same
admin handler — but the middleware sees them as non-admin paths and waves
them through without an auth check.

THE EXPLOIT
-----------
- ``GET /admin/users``                → middleware enforces auth ✅
- ``GET /Admin/users``                → middleware no-ops, framework still
                                        routes to admin_users handler ❌
- ``GET //admin/users``               → middleware sees ``//admin/...``
                                        which doesn't match the prefix ❌
- ``GET /admin/.;/users``             → matrix-param tricks vary by router.

THE FIX
-------
Either (a) apply the auth decorator on the *handler*, not the URL, or
(b) normalize the path before the prefix check (lowercase + collapse
slashes) — better still, lookup the route in the router first and ask
*it* whether the resolved view is admin-class.

WHY SAST MISSES IT
------------------
- CodeQL has nothing on "path normalization mismatch with framework
  routing" — it's a function of how *two* libraries disagree, not of one
  function's body.
- A pattern matcher would have to model every web framework's
  normalization rules vs every middleware's prefix-match. Nobody does.
- The vulnerability only exists when the middleware AND the router are
  both present and inconsistent — that's a global-system property.

This is a real CVE pattern (see CVE-2022-22965 routing edge cases, ASP.NET
double-slash, Express trust-proxy double-encoding bugs).
"""

from __future__ import annotations

from flask import Flask, abort, request

from .._auth_stub import is_admin

app = Flask(__name__)


@app.before_request
def enforce_admin_on_admin_paths() -> None:
    """Middleware: anything under /admin/ requires admin role."""
    # ❌ Naive prefix check. Doesn't normalize case, repeated slashes,
    # percent-encoding, or path traversal sequences. Flask's router still
    # dispatches /Admin/users to the same view — but this guard skips it.
    if request.path.startswith("/admin/"):
        if not is_admin():
            abort(403)


@app.route("/admin/users")
def admin_users():
    """Admin-only: list all users."""
    return {"users": ["alice", "bob"]}


@app.route("/admin/secrets")
def admin_secrets():
    return {"db_password": "should-not-leak"}
