# AgentGuard

AgentGuard is a pre-execution policy and anomaly firewall for agent-initiated
stablecoin payments. It checks whether a payment is authorized, policy-compliant,
consistent with recent behavior, and derived from a trustworthy source before it
reaches the execution layer.

## Quick start

The project targets Python 3.10 or newer. Set up a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Web demonstrator

The FastAPI demonstrator is a no-build browser UI. It uses server-sent events
to stream each decision and the simulated wallet balances to the page.

```bash
uvicorn app:app --reload
```

Open <http://localhost:8000>. The available demo scenarios are:

- `clean` — repeated payments to the approved merchant.
- `injected` — an invoice containing an indirect prompt injection.
- `adaptive` — a payment redirected to the attacker address.
- `stage-tour` — walks through mandate, policy, provenance, and anomaly cases.

The demo uses an in-memory `DemoChain`; it does not submit real transactions.

## Guard pipeline

Every request is evaluated in order:

1. **S0: Mandate** — verifies the user's signed mandate and expiry. Invalid
   signatures or expired mandates block immediately.
2. **S1: Policy** — checks maximum amount, rolling window budget, recipient
   allowlisting, and rate behavior. Hard violations block before execution.
3. **S2: Provenance** — derives taint from the payment request, user
   instruction, mandate, and tool results. A taint of `0.0` is trusted and
   `1.0` is untrusted.
4. **S3: Anomaly** — scores the request against rolling transaction features
   using River's streaming `HalfSpaceTrees` detector.

When S0 and S1 pass, the risk score is:

```text
score = 0.6 * anomaly + 0.3 * provenance_taint + 0.1 * soft_policy_flags
```

The default thresholds are `0.45` for `ALERT` and `0.75` for `BLOCK`.
Hard S0/S1 failures take priority over the weighted score. The demonstrator
transfers funds only for `ALLOW` and `ALERT` decisions; blocked requests never
reach its chain simulator.

## Repository guide

### `agentguard/` — core guard system

- `__init__.py` — package marker and public API surface.
- `agent.py` — simple payment-agent behavior.
- `chain.py` — simulated chain client for demo transactions.
- `detectors.py` — streaming anomaly detector using River's HalfSpaceTrees.
- `features.py` — payment feature extraction and rolling behavioral state.
- `guard.py` — `AgentGuard` class, session/config types, policy checks, risk scoring, and decision logic.
- `mandate.py` — mandate signing and signature/expiry verification.
- `tools.py` — payment request and tool-result models plus provenance-taint derivation.

### `core/` — integration layer

- `__init__.py` — package marker.
- `guard.py` — integration layer exposing `evaluate_payment` and `allow_all` used by the demo.

### `static/` and application root

- `app.py` — FastAPI server, demo scenarios, simulated wallet balances, and SSE streaming API.
- `static/index.html` — browser dashboard served at `/`.

### Project metadata

- `requirements.txt` — Python dependencies for Ethereum signing, anomaly detection, FastAPI, and web serving.
- `.gitignore` — files excluded from version control.
- `.venv/` — local Python virtual environment (created during setup, not part of source).

## Workflow

1. Activate `.venv` and install dependencies from `requirements.txt`.
2. Start the FastAPI app:
   ```bash
   uvicorn app:app --reload
   ```
3. Open <http://localhost:8000> in your browser.
4. Use the scenario controls to test different payment flows:
   - `clean` — repeated payments to the approved merchant.
   - `injected` — an invoice with indirect prompt injection.
   - `adaptive` — a payment redirected to the attacker address.
   - `stage-tour` — walks through each guard stage (mandate, policy, provenance, anomaly).

The demo uses an in-memory `DemoChain`; no live blockchain or external data is required.
