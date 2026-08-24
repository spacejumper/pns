from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class BenignPayment:
    recipient: str
    amount: int
    category: str


def generate_benign_payments(n: int = 1000, seed: int = 42) -> list[BenignPayment]:
    random.seed(seed)
    recipients = [
        "0x000000000000000000000000000000000000BEEF",
        "0x000000000000000000000000000000000000CAFE",
        "0x000000000000000000000000000000000000F00D",
    ]
    out: list[BenignPayment] = []
    for i in range(n):
        r = random.random()
        if r < 0.35:
            amount = random.randint(20, 80) * 1_000000
            category = "subscription"
            recipient = recipients[0]
        elif r < 0.7:
            amount = random.randint(1, 12) * 1_000000
            category = "api_micropayment"
            recipient = random.choice(recipients[:2])
        else:
            amount = random.randint(15, 190) * 1_000000
            category = "retail"
            recipient = random.choice(recipients)

        # Hard negative: near-cap but still legitimate.
        if i % 113 == 0:
            amount = 198 * 1_000000
            recipient = recipients[1]
            category = "large_legit"

        out.append(BenignPayment(recipient=recipient, amount=amount, category=category))
    return out
