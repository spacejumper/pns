# AgentGuard (PNS 2026 Topic 4 / Task 4)

AgentGuard is a pre-execution policy-and-anomaly firewall for agent-initiated stablecoin payments.
It is designed to evaluate:

- C1: intent-to-execution gap
- C3: adversarial robustness
- C4: latency vs intervention point

## Quick start

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the three experiment tracks:

```bash
python -m experiments.run_accuracy
python -m experiments.run_latency
python -m experiments.run_robustness
```

Outputs are written to `results/` as CSV and JSONL telemetry.

4. (Optional) Generate placeholder offline baseline output:

```bash
python -m experiments.run_elliptic_baseline
```

## Web demonstrator (FastAPI)

The repository includes a no-build browser demonstrator backed by FastAPI and
server-sent events. It runs the same guard logic as the experiment harness.

Start the web app:

```bash
uvicorn app:app --reload
```

Then open `http://localhost:8000`.

## How the guard works

The browser demonstrator and the experiment harness use the same guard
pipeline. Each payment request passes through four stages before execution:

- **S0 — Mandate:** verifies the user's signed mandate and checks that it has
  not expired. A failed signature or expired mandate blocks immediately.
- **S1 — Policy:** checks hard transaction constraints such as the maximum
  amount per transaction and the spending budget for the current time window.
  Recipient allowlisting and rate behavior also contribute policy signals. A
  hard policy violation blocks before the payment is sent.
- **S2 — Provenance:** measures whether the payment details came from an
  untrusted source, such as an invoice containing an indirect prompt injection.
  This produces a taint value from `0.0` (trusted) to `1.0` (untrusted).
- **S3 — Anomaly:** scores the request against the rolling transaction history
  using River's streaming `HalfSpaceTrees` detector. Larger values indicate
  behavior that is less consistent with the recent payment pattern.

If S0 and S1 pass, the guard combines the risk signals into one score:

```text
score = 0.6 × anomaly + 0.3 × provenance taint + 0.1 × soft-policy flags
```

The default block threshold is `0.75`. A score above the threshold produces a
`BLOCK`; otherwise the request is `ALLOW` or `ALERT` according to the alert
threshold. Hard S0/S1 failures take priority over the weighted score. A
blocked request is never transferred by the demonstrator's chain simulator;
an allowed or alert request is transferred and its balances are streamed to
the browser.

## Optional chain setup (Foundry + Anvil)

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
cd contracts
forge install OpenZeppelin/openzeppelin-contracts
anvil --block-time 1
```

## Repository map

- `agentguard/`: guard, features, detectors, mandate, telemetry
- `attacks/`: injection and evasion scenarios
- `workload/`: benign traffic generator
- `experiments/`: C1/C3/C4 runners
- `contracts/`: Solidity contracts and deploy script
- `results/`: generated outputs
- `app.py` and `static/`: FastAPI/SSE demonstrator UI for live decisions and system flow

## Reproducible workflow

1. Run experiments to refresh `results/*.csv`.
2. Start `agentguard-demo`.
3. Validate that dashboard cards/tables reflect the new experiment outputs.

## Notes

- This baseline ships with a deterministic simulator so metrics are reproducible without live chain dependencies.
- `agentguard/chain.py` contains a pluggable client wrapper for future Anvil integration.
- If only `table1_accuracy.csv` exists, the web UI shows placeholders for missing C3/C4 result files.
