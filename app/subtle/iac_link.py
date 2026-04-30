"""Code-IaC joint vulnerability: app uploads to a blob the IaC made public.

THE BUG
-------
This handler authenticates the user, then writes their per-user data into
Azure Blob Storage at ``users/{user_id}/data.bin``. The application
correctly enforces "user can only write their own folder".

But the storage account it writes into is the one declared in
``infra/main.bicep``, which has ``allowBlobPublicAccess: true``. *Anyone
on the Internet* can read every user's data via the direct blob URL,
without ever hitting this auth-checked endpoint.

THE EXPLOIT
-----------
- Legit user uploads ``users/42/data.bin`` via the app. App auth is fine.
- Attacker probes ``https://<account>.blob.core.windows.net/users/42/data.bin``.
- 200 OK. They have it.

The exploit doesn't go through the application at all. The application's
authentication is irrelevant because the blob is public at the
infrastructure layer.

WHY SAST MISSES IT
------------------
- Python SAST (CodeQL, Bandit) scans this file: clean — no obvious
  vulnerability. The auth check is correct, the path is sanitized, the
  blob client is used correctly.
- IaC SAST (Checkov, tfsec) scans ``infra/main.bicep``: it flags
  ``allowBlobPublicAccess: true`` as a generic risk.
- Neither tool *connects* the two: "the app trusts that this blob is
  private; the IaC says it isn't". That joint reasoning is what
  azure_full_stack_audit's cross-correlation stage exists for.

THE FIX
-------
Either disable public access on the storage account (correct) or change
the app to use SAS tokens with a short TTL and require authentication on
read (also correct). The combination of "private code path + public
storage" is a deployment defect, not a coding defect.
"""

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
    # ❌ App-side this is fine: auth ✓, path scoped to the user, blob client
    # used correctly. The vulnerability is in the deployment: this storage
    # account is public per infra/main.bicep:30 (allowBlobPublicAccess=true).
    # Everything written here is world-readable via the blob URL.
    _write_blob("stcodescandemo", "users", blob_path, request.get_data())
    return {"path": blob_path}


def _write_blob(account: str, container: str, path: str, data: bytes) -> None:
    """Stand-in for azure-storage-blob client."""
    pass
