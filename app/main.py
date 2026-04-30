"""Flask application — DELIBERATELY VULNERABLE.

Two pattern-detectable vulnerabilities live here. They are deliberately
the kind a regular SAST (CodeQL, SonarQube, GHAS) will catch — we want
the demo to show that CodeScan covers the standard SAST baseline before
we get to the genuinely-hard cases under ``app/subtle/``.
"""

from __future__ import annotations

import sqlite3

from flask import Flask, request

# CWE-798: hardcoded SECRET_KEY. Caught by every secret scanner / SAST.
# Included so the demo shows we don't *miss* the obvious cases.
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecret-change-me-but-dont-actually"  # noqa


@app.route("/users/search")
def users_search():
    """Search users by name. CWE-89: SQL injection via f-string.

    Textbook case — every SAST has a query for this.

    Attacker example: GET /users/search?q=' OR 1=1 --
    """
    q = request.args.get("q", "")
    cur = sqlite3.connect("app.db").cursor()
    cur.execute(f"SELECT id, name, email FROM users WHERE name LIKE '%{q}%'")
    return {"results": cur.fetchall()}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
