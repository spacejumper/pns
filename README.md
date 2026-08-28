# AgentGuard

AgentGuard is a pre-execution policy and anomaly firewall for agent-initiated
stablecoin payments. It checks whether a payment is authorized, policy-compliant,
consistent with recent behavior, and derived from a trustworthy source before it
reaches the execution layer.

The project evaluates three questions:

- **P1: Intent-to-execution gap** — can an agent turn an instruction into an
  unsafe payment?
- **P2: Adversarial robustness** — does the guard resist prompt injection and
  evasion scenarios?
- **P3: Latency and intervention point** — how much does each guard stage cost,
  and when does it stop a request?

## Quick start

The project targets Python 3.10 or newer. A virtual environment keeps the
experiment dependencies isolated:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run the experiment tracks from the repository root:

```bash
python -m experiments.run_accuracy
python -m experiments.run_latency
python -m experiments.run_robustness
```

The runners write CSV results to `results/`. The offline Elliptic baseline is
optional and produces a placeholder comparison when no external dataset is
available:

```bash
python -m experiments.run_elliptic_baseline
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

### `agentguard/` — primary Python guard package

- `__init__.py` — package marker and public package surface.
- `agent.py` — simple payment-agent behavior used by the experiments.
- `chain.py` — simulated chain client used for reproducible latency experiments
  and a future live-chain integration point.
- `detectors.py` — streaming anomaly detector implementation and detector
  results.
- `features.py` — payment feature extraction and rolling behavioral state.
- `guard.py` — `AgentGuard`, session/configuration types, policy checks, risk
  scoring, and `ALLOW`/`ALERT`/`BLOCK` decisions.
- `mandate.py` — mandate signing and signature/expiry verification.
- `tools.py` — payment request and tool-result models plus provenance-taint
  derivation.

### `core/` — compatibility guard surface

- `__init__.py` — package marker.
- `guard.py` — small integration layer exposing the guard entry points used by
  the experiment harness and demo (`evaluate_payment` and `allow_all`).

### `attacks/` — adversarial workloads

- `__init__.py` — package marker.
- `injections.py` — prompt-injection payload generation.
- `evasion.py` — adversarial and adaptive evasion cases.
- `scenarios.yaml` — attacker address and scenario levels (`A0` through `A5`).

### `workload/` — benign workloads

- `__init__.py` — package marker.
- `generator.py` — generation of normal payment traffic for comparison with
  adversarial traffic.

### `experiments/` — measurement scripts

- `__init__.py` — package marker.
- `common.py` — shared mandates, session bootstrap, metrics, CSV writing, and
  percentile helpers.
- `run_accuracy.py` — accuracy/confusion-matrix experiment.
- `run_latency.py` — latency measurement across guard stages.
- `run_robustness.py` — adversarial robustness experiment.
- `run_elliptic_baseline.py` — offline baseline comparison output.

### `static/` and root application

- `app.py` — FastAPI server, demo scenarios, simulated balances, and SSE API.
- `static/index.html` — browser dashboard served at `/`.

### `results/` — generated experiment output

CSV files such as `table1_accuracy.csv` are generated by the experiment
runners. `.gitkeep` preserves the directory when no generated output exists.

### Project metadata and local files

- `requirements.txt` — Python dependencies for Ethereum signing, anomaly
  detection, data analysis, FastAPI, and YAML scenarios.
- `.gitignore` — files excluded from version control.
- `.vscode/settings.json` — workspace-specific VS Code settings.
- `.venv/` — local Python virtual environment; created by setup and not part
  of the application source.

## Reproducible workflow

1. Activate `.venv` and install `requirements.txt`.
2. Run the experiment modules to refresh `results/*.csv`.
3. Start the FastAPI app and inspect the dashboard at `http://localhost:8000`.
4. Use the scenario controls to compare clean, injected, adaptive, and staged
   decisions.

No live blockchain or external dataset is required for the included baseline.
