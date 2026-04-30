"""Flask application — DELIBERATELY VULNERABLE.

Endpoints intentionally exhibit common web vulnerabilities so that the
CodeScan auditor has something concrete to find. Do not deploy this.
"""

from __future__ import annotations

import sqlite3
import subprocess
import urllib.parse
from urllib.request import urlopen

from flask import Flask, redirect, request

# CWE-798: Hardcoded credentials. The SECRET_KEY belongs in an env var
# loaded from a secrets manager — having it in source means anyone with
# read access to the repo can forge sessions.
app = Flask(__name__)
app.config["SECRET_KEY"] = "supersecret-change-me-but-dont-actually"  # noqa


def _get_db() -> sqlite3.Connection:
    return sqlite3.connect("app.db")


@app.route("/users/search")
def users_search():
    """Search users by name. CWE-89: SQL injection via f-string.

    Attacker example: GET /users/search?q=' OR 1=1 --
    """
    q = request.args.get("q", "")
    cur = _get_db().cursor()
    cur.execute(f"SELECT id, name, email FROM users WHERE name LIKE '%{q}%'")
    return {"results": cur.fetchall()}


@app.route("/ping")
def ping():
    """Diagnostic endpoint. CWE-78: command injection via shell=True.

    Attacker example: GET /ping?host=8.8.8.8;cat /etc/passwd
    """
    host = request.args.get("host", "127.0.0.1")
    out = subprocess.check_output(f"ping -c 1 {host}", shell=True, text=True)
    return {"output": out}


@app.route("/fetch")
def fetch():
    """Fetch a URL on behalf of the user. CWE-918: SSRF.

    No host allowlist — attackers can hit 169.254.169.254 (cloud metadata),
    internal admin services, etc.
    """
    target = request.args.get("url", "")
    with urlopen(target, timeout=5) as r:    # noqa: S310
        return r.read()


@app.route("/redirect")
def open_redirect():
    """Login redirect helper. CWE-601: open redirect.

    `next` is taken straight from the query string and used as the
    redirect target — phishing kits love this.
    """
    nxt = request.args.get("next", "/")
    return redirect(nxt)


@app.route("/render")
def render_template_unsafe():
    """Render a user-controlled template snippet. CWE-94: code injection
    via Jinja `render_template_string` on attacker input.
    """
    from flask import render_template_string

    tpl = request.args.get("tpl", "Hello {{ name }}!")
    return render_template_string(tpl, name=request.args.get("name", "world"))


@app.route("/exec")
def cmd_exec():
    """Internal automation hook. CWE-95: eval() on a query parameter."""
    code = request.args.get("expr", "1+1")
    return {"value": eval(code)}        # noqa: S307


if __name__ == "__main__":
    # CWE-489: debug mode exposes Werkzeug's interactive debugger, which is
    # a remote-code-execution panel by design.
    app.run(host="0.0.0.0", port=5000, debug=True)         # noqa: S104,S201
