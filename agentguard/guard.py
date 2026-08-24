from __future__ import annotations

import time
from dataclasses import dataclass, field

from agentguard.detectors import StreamingDetector
from agentguard.features import RollingState, extract_features
from agentguard.mandate import SignedMandate, verify_mandate
from agentguard.tools import PaymentRequest, ToolResult, derive_taint


@dataclass
class GuardConfig:
    theta_block: float = 0.75
    theta_alert: float = 0.45
    weight_anomaly: float = 0.6
    weight_taint: float = 0.3
    weight_soft_policy: float = 0.1
    max_rate_per_60s: int = 8


@dataclass
class GuardSession:
    signed_mandate: SignedMandate
    user_instruction: str
    rolling: RollingState = field(default_factory=RollingState)
    spent_in_window: int = 0
    window_started_at: float = 0.0


@dataclass
class GuardDecision:
    decision: str
    score: float
    reasons: list[str]
    latency_ms: float
    features: dict[str, float]
    anomaly_score: float = 0.0
    taint_score: float = 0.0
    soft_policy_flags: int = 0


class AgentGuard:
    def __init__(self, config: GuardConfig | None = None) -> None:
        self.config = config or GuardConfig()
        self.detector = StreamingDetector()

    def _check_policy(self, req: PaymentRequest, session: GuardSession, now: float) -> tuple[bool, list[str], int]:
        reasons: list[str] = []
        hard_violation = False
        mandate = session.signed_mandate.mandate

        max_per_tx = int(mandate["max_per_tx"])
        window_budget = int(mandate["window_budget"])
        window_seconds = int(mandate["window_seconds"])

        if session.window_started_at == 0 or now - session.window_started_at >= window_seconds:
            session.window_started_at = now
            session.spent_in_window = 0

        if req.amount > max_per_tx:
            hard_violation = True
            reasons.append("amount_above_max_per_tx")

        if session.spent_in_window + req.amount > window_budget:
            hard_violation = True
            reasons.append("window_budget_exceeded")

        allowed_recipients = {a.lower() for a in mandate.get("allowed_recipients", [])}
        if req.recipient.lower() not in allowed_recipients:
            reasons.append("recipient_not_allowlisted")

        soft_flags = 0
        if req.recipient.lower() not in allowed_recipients:
            soft_flags += 1

        if getattr(session.rolling, "_n_last_minute", 0) > self.config.max_rate_per_60s:
            reasons.append("rate_spike")
            soft_flags += 1

        return hard_violation, reasons, soft_flags

    def evaluate(
        self,
        req: PaymentRequest,
        session: GuardSession,
        tool_results: list[ToolResult],
    ) -> GuardDecision:
        t0 = time.perf_counter_ns()
        now = time.time()
        mandate_ok, mandate_reason = verify_mandate(session.signed_mandate)
        if not mandate_ok:
            t1 = time.perf_counter_ns()
            return GuardDecision(
                decision="BLOCK",
                score=1.0,
                reasons=[mandate_reason],
                latency_ms=(t1 - t0) / 1_000_000,
                features={},
            )

        hard_violation, policy_reasons, soft_flags = self._check_policy(req, session, now)
        if hard_violation:
            t1 = time.perf_counter_ns()
            return GuardDecision(
                decision="BLOCK",
                score=1.0,
                reasons=policy_reasons,
                latency_ms=(t1 - t0) / 1_000_000,
                features={},
            )

        taint = derive_taint(req, session.user_instruction, session.signed_mandate.mandate, tool_results)
        features = extract_features(
            amount=req.amount,
            recipient=req.recipient,
            taint=taint,
            now=now,
            max_per_tx=int(session.signed_mandate.mandate["max_per_tx"]),
            window_budget=int(session.signed_mandate.mandate["window_budget"]),
            state=session.rolling,
        )

        det = self.detector.score(features)
        score = (
            self.config.weight_anomaly * det.anomaly_score
            + self.config.weight_taint * taint
            + self.config.weight_soft_policy * float(soft_flags)
        )

        if score > self.config.theta_block:
            decision = "BLOCK"
        elif score > self.config.theta_alert:
            decision = "ALERT"
        else:
            decision = "ALLOW"

        reasons = [*policy_reasons, f"taint={taint:.2f}", f"anomaly={det.anomaly_score:.3f}"]
        if det.drift_flag:
            reasons.append("drift_detected")

        if decision in {"ALLOW", "ALERT"}:
            session.spent_in_window += req.amount

        t1 = time.perf_counter_ns()
        return GuardDecision(
            decision=decision,
            score=float(score),
            reasons=reasons,
            latency_ms=(t1 - t0) / 1_000_000,
            features=features,
            anomaly_score=det.anomaly_score,
            taint_score=taint,
            soft_policy_flags=soft_flags,
        )
