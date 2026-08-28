from __future__ import annotations

from dataclasses import asdict, dataclass

from agentguard.guard import AgentGuard, GuardSession
from agentguard.tools import PaymentRequest, ToolResult

__all__ = ["AgentGuard", "GuardSession", "Stage", "Verdict", "allow_all", "evaluate_payment"]


@dataclass
class Stage:
    name: str
    status: str
    value: float | None
    detail: str


@dataclass
class Verdict:
    seq: int
    recipient: str
    amount: float
    decision: str
    score: float
    threshold: float
    stages: list[Stage]
    latency_ms: float
    label: int
    anomaly_score: float = 0.0
    taint_score: float = 0.0
    soft_policy_flags: int = 0
    features: dict[str, float] | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def evaluate_payment(*, seq: int, request: PaymentRequest, session: GuardSession,
                     tool_results: list[ToolResult], guard: AgentGuard,
                     label: int, anomaly_override: float | None = None) -> Verdict:
    decision = guard.evaluate(req=request, session=session, tool_results=tool_results)
    if anomaly_override is not None and decision.features:
        decision.anomaly_score = anomaly_override
        decision.score = (
            guard.config.weight_anomaly * decision.anomaly_score
            + guard.config.weight_taint * decision.taint_score
            + guard.config.weight_soft_policy * float(decision.soft_policy_flags)
        )
        decision.decision = (
            "BLOCK" if decision.score > guard.config.theta_block
            else "ALERT" if decision.score > guard.config.theta_alert
            else "ALLOW"
        )
    reasons = decision.reasons
    mandate_failed = bool(reasons and reasons[0].startswith("mandate_"))
    policy_failed = any(reason in reasons for reason in (
        "recipient_not_allowlisted", "amount_above_max_per_tx", "window_budget_exceeded"
    ))
    taint = float(decision.features.get("taint_score", 0.0))
    policy_status = "fail" if policy_failed else ("score" if mandate_failed else "pass")
    if "amount_above_max_per_tx" in reasons or "window_budget_exceeded" in reasons:
        policy_detail = "amount exceeds approved limit"
    elif "recipient_not_allowlisted" in reasons:
        policy_detail = "recipient not in approved set"
    else:
        policy_detail = "recipient and amount approved"
    provenance_status = "fail" if taint >= 0.75 else "pass"
    provenance_detail = "first seen in untrusted invoice source" if provenance_status == "fail" else "trusted instruction or known source"
    if not decision.features:
        provenance_status = "score"
        provenance_detail = "not reached after hard policy decision"
    stages = [
        Stage("S0 mandate", "fail" if mandate_failed else "pass", None,
              "signature rejected" if mandate_failed else "valid signature and active expiry"),
        Stage("S1 policy", policy_status, None, policy_detail),
        Stage("S2 provenance", provenance_status, taint, provenance_detail),
        Stage("S3 anomaly", "fail" if not (mandate_failed or policy_failed) and decision.score > guard.config.theta_block else "score", decision.anomaly_score,
              "Computed from the payment's recent behavioral history."),
    ]
    return Verdict(
        seq=seq, recipient=request.recipient, amount=request.amount / 1_000_000,
        decision="allow" if decision.decision == "ALERT" else decision.decision.lower(),
        score=float(decision.score),
        threshold=guard.config.theta_block, stages=stages,
        latency_ms=max(0.1, decision.latency_ms), label=label,
        anomaly_score=decision.anomaly_score, taint_score=decision.taint_score,
        soft_policy_flags=decision.soft_policy_flags,
        features=decision.features,
    )


def allow_all(*, seq: int, request: PaymentRequest, label: int) -> Verdict:
    return Verdict(
        seq=seq, recipient=request.recipient, amount=request.amount / 1_000_000,
        decision="allow", score=0.0, threshold=0.0, latency_ms=0.3, label=label,
        stages=[
            Stage("S0 mandate", "pass", None, "guard bypassed"),
            Stage("S1 policy", "pass", None, "guard bypassed"),
            Stage("S2 provenance", "pass", 0.0, "guard bypassed"),
            Stage("S3 anomaly", "score", 0.0, "post-execution alert path"),
        ],
    )