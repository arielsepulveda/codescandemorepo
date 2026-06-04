"""Per-user data upload endpoint."""

from __future__ import annotations

from flask import Blueprint, abort, request

from .._auth_stub import current_user

uploads_bp = Blueprint("user_uploads", __name__)


@uploads_bp.route("/users/me/data", methods=["POST"])
def upload_my_data():
    user = current_user()
    if user is None:
        abort(401)

    blob_path = f"users/{user.id}/data.bin"
    _write_blob("stcodescandemo", "users", blob_path, request.get_data())
    return {"path": blob_path}


def _write_blob(account: str, container: str, path: str, data: bytes) -> None:
    """Stand-in for azure-storage-blob client."""
    pass
