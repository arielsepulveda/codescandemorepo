"""User profile API."""

from __future__ import annotations

import json
from flask import Blueprint, jsonify, request

bp = Blueprint("cross_lang", __name__)


@bp.route("/api/me")
def get_me():
    user_id = request.args.get("user_id")
    is_admin = _check_admin(user_id)
    return jsonify({
        "id": user_id,
        "name": "Alice",
        "is_admin": str(is_admin).lower(),
    })


def _check_admin(user_id: str | None) -> bool:
    return user_id == "1"
