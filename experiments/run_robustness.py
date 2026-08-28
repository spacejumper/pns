from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from attacks.evasion import (
    generate_a2_split,
    generate_a3_slow_drip,
    generate_a4_warm_then_drain,
    generate_a5_feature_aware,
)
from attacks.injections import payload_a0, payload_a1
from experiments.common import bootstrap_session, write_csv


ATTACKER = "0x000000000000000000000000000000000000DEAD"


def main() -> None:
    guard, session, agent = bootstrap_session()

    totals = defaultdict(int)
    blocked = defaultdict(int)

    # A0/A1 via direct prompt-injection payloads.
    for level, payload in [("A0", payload_a0(ATTACKER)), ("A1", payload_a1(ATTACKER))]:
        for i in range(20):
            out = agent.run(invoice_id=f"{level}-{i}", injected_payload=payload)
            decision = guard.evaluate(req=out.payment, session=session, tool_results=out.tool_results)
            totals[level] += 1
            if decision.decision == "BLOCK":
                blocked[level] += 1

    # A2-A5 via behavior-level evasion steps.
    recipes = {
        "A2": generate_a2_split(ATTACKER),
        "A3": generate_a3_slow_drip(ATTACKER),
        "A4": generate_a4_warm_then_drain(ATTACKER),
        "A5": generate_a5_feature_aware(ATTACKER),
    }

    from agentguard.tools import pay

    for level, steps in recipes.items():
        for _ in range(10):
            for s in steps:
                req = pay(s.recipient, s.amount, s.note)
                decision = guard.evaluate(req=req, session=session, tool_results=[])
                totals[level] += 1
                if decision.decision == "BLOCK":
                    blocked[level] += 1

    rows = []
    for level in ["A0", "A1", "A2", "A3", "A4", "A5"]:
        t = totals[level]
        b = blocked[level]
        recall = b / t if t else 0.0
        rows.append(
            {
                "attack_level": level,
                "recall": f"{recall:.4f}",
                "blocked": b,
                "total": t,
            }
        )

    write_csv(Path("results/table3_robustness.csv"), rows)
    print("Wrote results/table3_robustness.csv")


if __name__ == "__main__":
    main()
