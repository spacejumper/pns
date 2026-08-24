from __future__ import annotations

from pathlib import Path

from attacks.injections import payload_a0, payload_a1
from experiments.common import Record, bootstrap_session, confusion, write_csv
from workload.generator import generate_benign_payments


def main() -> None:
    guard, session, logger, llm_agent = bootstrap_session()

    records: list[Record] = []
    seq = 0

    for payment in generate_benign_payments(n=1000):
        seq += 1
        from agentguard.tools import pay

        req = pay(payment.recipient, payment.amount, f"{payment.category} payment")
        decision = guard.evaluate(req=req, session=session, tool_results=[])
        pred = 1 if decision.decision == "BLOCK" else 0
        records.append(Record(label=0, prediction=pred, score=decision.score))

    injections = [payload_a0(), payload_a1()]
    for i in range(120):
        seq += 1
        payload = injections[i % len(injections)]
        out = llm_agent.run(invoice_id=f"inj-{i}", injected_payload=payload)
        decision = guard.evaluate(req=out.payment, session=session, tool_results=out.tool_results)
        pred = 1 if decision.decision == "BLOCK" else 0
        records.append(Record(label=1, prediction=pred, score=decision.score))

    stats = confusion(records)
    rows = [{
        "model": "rules_taint_hst",
        "precision": f"{stats['precision']:.4f}",
        "recall": f"{stats['recall']:.4f}",
        "f1": f"{stats['f1']:.4f}",
        "fpr": f"{stats['fpr']:.4f}",
    }]
    write_csv(Path("results/table1_accuracy.csv"), rows)
    print("Wrote results/table1_accuracy.csv")


if __name__ == "__main__":
    main()
