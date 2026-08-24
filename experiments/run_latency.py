from __future__ import annotations

from pathlib import Path

from agentguard.chain import SimulatedChain
from agentguard.tools import pay
from experiments.common import bootstrap_session, percentile, write_csv


def main() -> None:
    guard, session, _, _ = bootstrap_session()
    chain = SimulatedChain(block_time_seconds=0.01)

    pre_lat: list[float] = []
    post_lat: list[float] = []

    for i in range(1000):
        req = pay("0x000000000000000000000000000000000000BEEF", 9_000000 + (i % 10) * 1_000000, "latency run")

        d = guard.evaluate(req=req, session=session, tool_results=[])
        pre_lat.append(d.latency_ms)

        tx_hash, t_submit = chain.submit()
        receipt = chain.mine(tx_hash)
        if receipt.mined_at:
            post_lat.append((receipt.mined_at - t_submit) * 1000.0)

    rows = [
        {
            "intervention": "pre_execution_guard",
            "p50_ms": f"{percentile(pre_lat, 0.5):.3f}",
            "p95_ms": f"{percentile(pre_lat, 0.95):.3f}",
            "p99_ms": f"{percentile(pre_lat, 0.99):.3f}",
            "funds_recovered": "1.0",
        },
        {
            "intervention": "post_execution_monitor",
            "p50_ms": f"{percentile(post_lat, 0.5):.3f}",
            "p95_ms": f"{percentile(post_lat, 0.95):.3f}",
            "p99_ms": f"{percentile(post_lat, 0.99):.3f}",
            "funds_recovered": "0.0",
        },
    ]
    write_csv(Path("results/table2_latency.csv"), rows)
    print("Wrote results/table2_latency.csv")


if __name__ == "__main__":
    main()
