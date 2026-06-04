"""Async money-transfer endpoint."""

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
    src = await accounts.get(from_user_id)
    if src.balance < amount:
        return {"ok": False, "reason": "insufficient funds"}

    await notify_user(from_user_id, f"transfer of {amount} initiated")

    src.balance -= amount
    await accounts.save(src)
    dst = await accounts.get(to_user_id)
    dst.balance += amount
    await accounts.save(dst)
    return {"ok": True}
