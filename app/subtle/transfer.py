"""Business-logic TOCTOU in an async transfer endpoint.

THE BUG
-------
Bank-style transfer. The handler reads the balance, checks it covers the
requested amount, awaits a notification side-effect, then debits. Two
concurrent requests from the same user can both pass the check, then both
debit — overdrawing the account.

THE EXPLOIT
-----------
- User has $1000. Open two HTTP/2 streams.
- Send POST /transfer with amount=$800 on each, near-simultaneously.
- Both check `1000 >= 800` (True) before either debits.
- Both await notify_user (~200ms each, no DB lock during).
- Both debit. Final balance: -$600.

Real systems hide this in payments, gift cards, internal credits, voucher
redemption. The exploit window scales with notify latency.

WHY SAST MISSES IT
------------------
- This race lives in *I/O ordering*, not in a `threading.Lock` omission.
  CodeQL has race-condition queries for filesystem TOCTOU and for the
  `os.access → open` pattern — none for "balance read, await, balance
  write" in async code, because that's a per-domain invariant.
- The fix is "use a database transaction with SELECT ... FOR UPDATE, or an
  optimistic concurrency token, or a row-level lock". Knowing which is
  appropriate requires reading the *purpose* of the function — that's
  semantic.
"""

from __future__ import annotations

import asyncio

from .._db_stub import accounts


async def notify_user(user_id: int, message: str) -> None:
    """Push notification — slow (network)."""
    await asyncio.sleep(0.2)


async def transfer(from_user_id: int, to_user_id: int, amount: float) -> dict:
    """Move ``amount`` from one account to another.

    Invariant we want: balance never goes negative.
    """
    src = await accounts.get(from_user_id)         # read 1
    if src.balance < amount:
        return {"ok": False, "reason": "insufficient funds"}

    # ❌ Anything the developer puts here that yields control opens a TOCTOU
    # window — and there's no static signature for "yield control between
    # check and write". Two requests interleave at this await point.
    await notify_user(from_user_id, f"transfer of {amount} initiated")

    # By the time we get here, another concurrent request may already have
    # debited based on its own (now stale) read.
    src.balance -= amount                          # write 1 (no lock)
    await accounts.save(src)
    dst = await accounts.get(to_user_id)
    dst.balance += amount
    await accounts.save(dst)
    return {"ok": True}
