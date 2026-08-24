from __future__ import annotations

import csv
import os
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

from eth_account import Account

from agentguard.agent import SimplePaymentAgent
from core.guard import AgentGuard, GuardSession
from agentguard.mandate import sign_mandate
from agentguard.telemetry import TelemetryEvent, TelemetryLogger


RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


@dataclass
class Record:
    label: int
    prediction: int
    score: float


def default_mandate(agent_address: str, user_address: str) -> dict:
    return {
        "version": "1",
        "user": user_address,
        "agent": agent_address,
        "max_per_tx": 200_000000,
        "window_budget": 500_000000,
        "window_seconds": 86400,
        "allowed_recipients": [
            "0x000000000000000000000000000000000000BEEF",
            "0x000000000000000000000000000000000000CAFE",
        ],
        "allowed_categories": ["saas", "api_credits", "retail"],
        "expiry": int(time.time()) + 86400,
        "nonce": "0x" + "11" * 32,
    }


def bootstrap_session() -> tuple[AgentGuard, GuardSession, TelemetryLogger, SimplePaymentAgent]:
    user = Account.create()
    agent = Account.create()
    mandate = default_mandate(agent.address, user.address)
    signed = sign_mandate(mandate, user.key.hex())
    session = GuardSession(signed_mandate=signed, user_instruction="Pay monthly invoice to approved recipient")
    guard = AgentGuard()
    logger = TelemetryLogger(RESULTS_DIR / "telemetry.jsonl")
    llm_agent = SimplePaymentAgent(scripted=True)
    return guard, session, logger, llm_agent


def confusion(records: list[Record]) -> dict[str, float]:
    tp = sum(1 for r in records if r.label == 1 and r.prediction == 1)
    fp = sum(1 for r in records if r.label == 0 and r.prediction == 1)
    tn = sum(1 for r in records if r.label == 0 and r.prediction == 0)
    fn = sum(1 for r in records if r.label == 1 and r.prediction == 0)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    k = (len(values) - 1) * p
    floor = int(k)
    ceil = min(floor + 1, len(values) - 1)
    if floor == ceil:
        return values[floor]
    return values[floor] + (values[ceil] - values[floor]) * (k - floor)
