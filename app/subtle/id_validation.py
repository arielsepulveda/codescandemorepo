"""Profile lookup endpoint."""

from __future__ import annotations

from flask import Blueprint, abort, jsonify, request

from .._db_stub import Profile

profiles = Blueprint("profiles", __name__)


def _validate_user_id(raw: str) -> int:
    """Cast the query string into an int."""
    try:
        return int(raw)
    except (TypeError, ValueError):
        abort(400)


@profiles.route("/api/profile")
def get_profile():
    user_id = _validate_user_id(request.args.get("user_id", ""))
    profile = Profile.objects.filter(id=user_id).first()
    if profile is None:
        abort(404)
    return jsonify(profile.to_dict())
