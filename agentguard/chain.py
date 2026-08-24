from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TxReceipt:
    tx_hash: str
    mined: bool
    mined_at: float | None


class SimulatedChain:
    """Simple chain simulator for local reproducible latency experiments."""

    def __init__(self, block_time_seconds: float = 1.0) -> None:
        self.block_time_seconds = block_time_seconds
        self._counter = 0

    def submit(self) -> tuple[str, float]:
        self._counter += 1
        tx_hash = f"0xSIM{self._counter:08d}"
        return tx_hash, time.time()

    def mine(self, tx_hash: str) -> TxReceipt:
        time.sleep(self.block_time_seconds)
        return TxReceipt(tx_hash=tx_hash, mined=True, mined_at=time.time())
