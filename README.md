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

Then open `http://localhost:3000`.

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
- `agentguard-demo/`: Next.js demonstrator UI for metrics and system flow

## Reproducible workflow

1. Run experiments to refresh `results/*.csv`.
2. Start `agentguard-demo`.
3. Validate that dashboard cards/tables reflect the new experiment outputs.

## Notes

- This baseline ships with a deterministic simulator so metrics are reproducible without live chain dependencies.
- `agentguard/chain.py` contains a pluggable client wrapper for future Anvil integration.
- If only `table1_accuracy.csv` exists, the web UI shows placeholders for missing C3/C4 result files.
