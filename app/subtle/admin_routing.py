"""Admin area: routing + a before-request guard."""

from __future__ import annotations

from flask import Flask, abort, request

from .._auth_stub import is_admin

app = Flask(__name__)


@app.before_request
def enforce_admin_on_admin_paths() -> None:
    """Middleware: anything under /admin/ requires admin role."""
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
