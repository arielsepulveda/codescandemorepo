"""Record-read endpoint: admins may read any record, users only their own."""

from __future__ import annotations

from flask import Blueprint, abort, jsonify, request

from .._auth_stub import current_user, lookup_record

records = Blueprint("records", __name__)


@records.route("/records/read", methods=["POST"])
def read_record():
    """Read a record. Admins: any record. Users: only their own."""
    body = request.get_json() or {}
    target_id: int = body["target_id"]
    is_admin_request: bool = body.get("as_admin", False)

    if is_admin_request or current_user().id == target_id:
        return jsonify(lookup_record(target_id))
    abort(403)
