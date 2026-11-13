"""Design inputs for the v4 decision endpoint (population level, split 99 only).

For each split-99 graph and each non-null structure at the v4 main setting, it
computes the population probability that the CI-only rule (P0, all 16,384
shots on the targets) certifies the wrong winner, and the probability that it
certifies at all. It uses exact noisy means and variances and a Gaussian
approximation of the sample gap. No shot is drawn and no probe statistic is
used.  Main settings follow the v3/v4 sign rule applied to the split-99
medians in experiments/design_checks (E2 +0.04, E3 -0.04); readout signs do
not change these probabilities.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "audit"))

import channels  # noqa: E402
import execution  # noqa: E402
import manifest  # noqa: E402
import p0_unresolved_audit as audit  # noqa: E402
import simulate  # noqa: E402

MAIN = {
    "E1": "0.04",
    "E2": "0.04",
    "E3": "-0.04",
    "E4": "(0.08,0.12)",
    "E5": "0.01",
    "E5'": "0.015625",
    "E6": "0.03",
}


def moments(record, structure, setting, cache):
    condition = channels.parse_condition(structure, setting)
    scores = simulate.cut_scores(record.width, record.edges)
    m, v = [], []
    for circuit in execution.target_circuits("software_test", record, condition):
        p = audit.post_distribution(record, condition, cache, circuit)
        mean = float(p @ scores)
        m.append(mean)
        v.append(float(p @ scores**2) - mean * mean)
    return m[0] - m[1], math.sqrt((v[0] + v[1]) / audit.N_EACH)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "experiments" / "power" / "decision_design_inputs_v5.csv",
    )
    args = parser.parse_args()
    if args.output.exists():
        print(f"Refusing to overwrite existing output: {args.output}")
        return 1
    cache = execution.SolveCache()
    rows = []
    for record in manifest.build_manifest("software_test", REPO):
        ideal, _ = moments(record, "E0", "0.0", cache)
        sign = np.sign(ideal)
        for structure, setting in MAIN.items():
            mu, sigma = moments(record, structure, setting, cache)
            z = mu * sign
            wrong = audit.phi((-2 * audit.H - z) / sigma)
            right = 1 - audit.phi((2 * audit.H - z) / sigma)
            rows.append(
                {
                    "graph_id": record.graph_id,
                    "width": record.width,
                    "depth": record.depth,
                    "structure": structure,
                    "setting": setting,
                    "ideal_gap": repr(ideal),
                    "noisy_gap": repr(mu),
                    "p_false_certification": repr(wrong),
                    "p_certification": repr(wrong + right),
                    "flipped": int(z <= 0),
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
