"""Customer-support LLM agent endpoint."""

from __future__ import annotations

from typing import Any


class CustomerSupportLLM:
    """Stand-in for a real agent runtime."""

    def run(self, messages: list[dict], tools: list[Any]) -> Any: ...


def cancel_subscription(user_id: int) -> dict: ...
def issue_refund(user_id: int, amount: float) -> dict: ...
def escalate_to_human(ticket_id: int) -> dict: ...
def read_customer_record(user_id: int) -> dict: ...


SYSTEM_PROMPT = """\
You are a customer-support agent. Help the user. You may call tools to
take actions on their behalf when appropriate.
"""


def customer_support_agent(user_message: str) -> Any:
    """Handle a customer message in plain English, with tools available."""
    llm = CustomerSupportLLM()
    return llm.run(
        messages=[
            {"role": "system",  "content": SYSTEM_PROMPT},
            {"role": "user",    "content": user_message},
        ],
        tools=[
            cancel_subscription,
            issue_refund,
            escalate_to_human,
            read_customer_record,
        ],
    )
