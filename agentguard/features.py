from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from statistics import median


@dataclass
class RollingState:
    amounts: deque[int] = field(default_factory=lambda: deque(maxlen=256))
    recipients_last_hour: deque[tuple[float, str]] = field(default_factory=deque)
    tx_times: deque[float] = field(default_factory=deque)
    window_spent: int = 0
    window_start: float = 0.0
    recipient_counts: dict[str, int] = field(default_factory=dict)


def _prune(state: RollingState, now: float) -> None:
    one_hour_ago = now - 3600
    one_min_ago = now - 60
    while state.recipients_last_hour and state.recipients_last_hour[0][0] < one_hour_ago:
        state.recipients_last_hour.popleft()
    while state.tx_times and state.tx_times[0] < one_hour_ago:
        state.tx_times.popleft()
    state._n_last_minute = sum(1 for t in state.tx_times if t >= one_min_ago)


def extract_features(
    *,
    amount: int,
    recipient: str,
    taint: float,
    now: float,
    max_per_tx: int,
    window_budget: int,
    state: RollingState,
) -> dict[str, float]:
    if state.window_start == 0:
        state.window_start = now

    _prune(state, now)

    med = float(median(state.amounts)) if state.amounts else float(max(1, amount))
    seconds_since_last = now - state.tx_times[-1] if state.tx_times else 1e9
    recipient_seen_count = state.recipient_counts.get(recipient.lower(), 0)
    unique_recipients_1h = len({r for _, r in state.recipients_last_hour})

    features = {
        "log1p_amount": math.log1p(amount),
        "amount_over_max_per_tx": float(amount) / max(1.0, float(max_per_tx)),
        "amount_over_rolling_median": float(amount) / max(1.0, med),
        "recipient_seen_count": float(recipient_seen_count),
        "seconds_since_last_payment": float(seconds_since_last),
        "n_payments_last_60s": float(getattr(state, "_n_last_minute", 0)),
        "n_payments_last_1h": float(len(state.tx_times)),
        "window_spent_ratio": float(state.window_spent) / max(1.0, float(window_budget)),
        "n_recipients_last_1h": float(unique_recipients_1h),
        "taint_score": float(taint),
    }

    state.amounts.append(amount)
    state.tx_times.append(now)
    state.recipients_last_hour.append((now, recipient.lower()))
    state.recipient_counts[recipient.lower()] = recipient_seen_count + 1

    return features
