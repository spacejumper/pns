from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvasionStep:
    level: str
    recipient: str
    amount: int
    note: str


def generate_a2_split(recipient: str, n: int = 5, amount_each: int = 195_000000) -> list[EvasionStep]:
    return [EvasionStep(level="A2", recipient=recipient, amount=amount_each, note=f"split_{i}") for i in range(n)]


def generate_a3_slow_drip(recipient: str, n: int = 6, amount_each: int = 80_000000) -> list[EvasionStep]:
    return [EvasionStep(level="A3", recipient=recipient, amount=amount_each, note=f"drip_{i}") for i in range(n)]


def generate_a4_warm_then_drain(recipient: str) -> list[EvasionStep]:
    return [
        EvasionStep(level="A4", recipient=recipient, amount=5_000000, note="warm_1"),
        EvasionStep(level="A4", recipient=recipient, amount=7_000000, note="warm_2"),
        EvasionStep(level="A4", recipient=recipient, amount=9_000000, note="warm_3"),
        EvasionStep(level="A4", recipient=recipient, amount=180_000000, note="drain"),
    ]


def generate_a5_feature_aware(recipient: str) -> list[EvasionStep]:
    # Keep transactions under thresholds and close to median-like values.
    return [
        EvasionStep(level="A5", recipient=recipient, amount=45_000000, note="camouflage_1"),
        EvasionStep(level="A5", recipient=recipient, amount=52_000000, note="camouflage_2"),
        EvasionStep(level="A5", recipient=recipient, amount=48_000000, note="camouflage_3"),
        EvasionStep(level="A5", recipient=recipient, amount=60_000000, note="camouflage_4"),
    ]
