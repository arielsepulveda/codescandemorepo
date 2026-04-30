"""Upload + processing endpoints — DELIBERATELY VULNERABLE."""

from __future__ import annotations

import os
import pickle

from flask import Blueprint, request, send_file

uploads = Blueprint("uploads", __name__)

UPLOAD_ROOT = "/var/data/uploads"


@uploads.route("/upload", methods=["POST"])
def upload_file():
    """CWE-22: path traversal via user-controlled filename.

    `request.form["filename"]` may be `../../etc/cron.d/evil`.
    CWE-434: no extension / MIME validation either.
    """
    f = request.files["file"]
    name = request.form["filename"]                 # untrusted
    target = os.path.join(UPLOAD_ROOT, name)        # naive join
    f.save(target)
    return {"saved": target}


@uploads.route("/download")
def download_file():
    """CWE-22: same class as above on read path.

    `name=../../../../etc/passwd` reads from outside UPLOAD_ROOT.
    """
    name = request.args.get("name", "")
    return send_file(os.path.join(UPLOAD_ROOT, name))


@uploads.route("/process", methods=["POST"])
def process_blob():
    """CWE-502: deserialize untrusted pickle => arbitrary RCE.

    pickle.loads on attacker-controlled bytes is RCE; no amount of "we
    only accept pickles from authenticated users" makes this safe — auth
    cookies leak, JWTs get forged, etc.
    """
    blob = request.get_data()
    obj = pickle.loads(blob)                 # noqa: S301
    return {"type": type(obj).__name__}


@uploads.route("/extract", methods=["POST"])
def extract_archive():
    """CWE-22 + CWE-409 (zip slip / zip bomb).

    `tarfile.extractall` without member sanitization writes anywhere a
    crafted tar entry points (../../etc/passwd).
    """
    import tarfile

    f = request.files["archive"]
    f.save("/tmp/in.tar")
    with tarfile.open("/tmp/in.tar") as t:
        t.extractall(UPLOAD_ROOT)            # noqa: S202
    return {"ok": True}
