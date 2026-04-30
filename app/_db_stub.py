"""Placeholder DB / ORM helpers for the subtle/ demos."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Account:
    user_id: int
    balance: float


class _AccountsAsync:
    async def get(self, user_id: int) -> Account: ...
    async def save(self, account: Account) -> None: ...


accounts = _AccountsAsync()


class _ProfileQuery:
    def filter(self, **kw: Any) -> "_ProfileQuery": return self
    def first(self) -> Any: return None


@dataclass
class _ProfileObjects:
    objects: _ProfileQuery


class Profile:
    objects: _ProfileQuery = _ProfileQuery()

    def to_dict(self) -> dict[str, Any]:
        return {}
