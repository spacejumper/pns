from __future__ import annotations

from pathlib import Path

from experiments.common import write_csv


def main() -> None:
    # Placeholder for future Elliptic++ integration. This keeps report wiring stable.
    rows = [
        {
            "dataset": "ellipticpp_placeholder",
            "model": "random_forest",
            "pr_auc": "0.0000",
            "note": "Populate after integrating Elliptic++ data loader",
        }
    ]
    write_csv(Path("results/elliptic_baseline.csv"), rows)
    print("Wrote results/elliptic_baseline.csv")


if __name__ == "__main__":
    main()
