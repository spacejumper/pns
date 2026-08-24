from __future__ import annotations

from dataclasses import dataclass

from agentguard.tools import PaymentRequest, fetch_invoice, pay


@dataclass
class AgentRunOutput:
    payment: PaymentRequest
    tool_results: list


class SimplePaymentAgent:
    """Minimal tool-using agent for deterministic experiments."""

    def __init__(self, scripted: bool = True) -> None:
        self.scripted = scripted

    def run(self, invoice_id: str, injected_payload: str | None = None) -> AgentRunOutput:
        invoice = fetch_invoice(invoice_id=invoice_id, injected_payload=injected_payload)
        if injected_payload:
            # Very simple parser for attack payloads of shape recipient=... amount=...
            recipient = "0x000000000000000000000000000000000000BEEF"
            amount = 49_000000
            for token in injected_payload.split():
                if token.startswith("recipient="):
                    recipient = token.split("=", 1)[1]
                if token.startswith("amount="):
                    amount = int(token.split("=", 1)[1])
            req = pay(recipient=recipient, amount=amount, memo="scripted injected payment")
        else:
            req = pay(
                recipient="0x000000000000000000000000000000000000BEEF",
                amount=49_000000,
                memo="legit invoice payment",
            )
        return AgentRunOutput(payment=req, tool_results=[invoice])
