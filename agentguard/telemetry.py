from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any


@dataclass
class TelemetryEvent:
    episode: str
    seq: int
    label: int
    attack: str
    amount: int
    recipient: str
    decision: str
    score: float
    reasons: list[str] = field(default_factory=list)
    t_request: float = 0.0
    t_decision: float = 0.0
    t_broadcast: float | None = None
    t_mined: float | None = None


class TelemetryLogger:
    def __init__(self, output_path: str | Path) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def now() -> float:
        return time.time()

    @staticmethod
    def perf_ns() -> int:
        return time.perf_counter_ns()

    def log(self, event: TelemetryEvent, extra: dict[str, Any] | None = None) -> None:
        payload = asdict(event)
        if extra:
            payload.update(extra)
        with self.output_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, sort_keys=True) + "\n")
