"""Negative-ID ORM bypass — passes every "input is sanitized" check.

THE BUG
-------
The validator coerces user input to ``int``. The downstream ORM query uses
that int as a primary-key filter. A negative id passes the validator
(it's a valid int, doesn't trigger the SQLi sink) but the ORM accepts it
and returns the row whose internal counter wraps to that value, OR — if
the table has ``BIGINT signed`` keys — returns the row of the user whose
id is the absolute value, depending on how the ORM maps comparisons.

THE EXPLOIT
-----------
- Endpoint: GET /api/profile?user_id=-1
- Validator: `int(request.args["user_id"])` → -1 → no exception.
- ORM: ``Profile.objects.filter(id=-1).first()`` → in some legacy schemas,
  -1 is the row of the system superuser. In well-modeled schemas it's None,
  but if the code does `.get(id=request.args["user_id"], visibility__lte=
  request.args["user_id"])` the negative number flips the visibility filter.

Even when the immediate query is benign, downstream code that does
``"-1" in user_id`` or ``user_id < 0`` for "system" lookups gets surprised.

WHY SAST MISSES IT
------------------
- CodeQL: this is taint-clean. ``int(...)`` is a recognized sanitizer for
  most query libraries; CodeQL strips the taint at that node.
- The *attack* is semantic — "negative ids are out of the legal domain
  for *this* model" — and only a reviewer who knows the data model can
  tell. SAST would have to encode that invariant per-model, which is what
  developers already fail to do.

THE RIGHT FIX
-------------
Validate against the legal domain (``id > 0``), not against the type. Or
use a typed primary key (UUID) where negative is structurally impossible.
"""

from __future__ import annotations

from flask import Blueprint, abort, jsonify, request

from .._db_stub import Profile

profiles = Blueprint("profiles", __name__)


def _validate_user_id(raw: str) -> int:
    """Cast the query string into an int. Pattern SAST treats this as a
    sanitizer because it eliminates string-injection paths.
    """
    try:
        return int(raw)
    except (TypeError, ValueError):
        abort(400)


@profiles.route("/api/profile")
def get_profile():
    user_id = _validate_user_id(request.args.get("user_id", ""))
    # ❌ The validator returned an int but didn't enforce id > 0. The ORM
    # accepts negative ids; the row at id=-1 belongs to a seed-data
    # "system" account with elevated visibility on this schema.
    profile = Profile.objects.filter(id=user_id).first()
    if profile is None:
        abort(404)
    return jsonify(profile.to_dict())
