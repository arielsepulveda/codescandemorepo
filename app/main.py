"""Flask application — user search API."""

from __future__ import annotations

import sqlite3

from flask import Flask, request

app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecret-change-me-but-dont-actually"


@app.route("/users/search")
def users_search():
    """Search users by name."""
    q = request.args.get("q", "")
    cur = sqlite3.connect("app.db").cursor()
    cur.execute(f"SELECT id, name, email FROM users WHERE name LIKE '%{q}%'")
    return {"results": cur.fetchall()}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
