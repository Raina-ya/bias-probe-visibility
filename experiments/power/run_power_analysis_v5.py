"""Power analysis v5 for the v4 decision endpoint (non-circular).

No prediction-matrix label sets any mean.  Inputs are the population-level
split-99 design inputs (decision_design_inputs_v5.csv): per graph and structure,
the CI-only false-certification and certification probabilities.  The unknown
probe behaviour is a frozen grid: detection probability d on flipped graphs and
alarm probability a on non-flipped graphs.  A stress factor k multiplies the
CI-only false-certification probabilities (capped at the certification
probability) to cover a holdout graph mix less favourable than split 99.

Per simulated dataset: 100 graphs drawn with replacement from the 50 split-99
graphs, 32 repeats per graph and structure, Bernoulli outcomes for the CI-only
rule R0 and the bias-aware rule R1, the pooled estimand (equal structure
weights), and a 1,000-resample graph-cluster bootstrap with shared indices.
The prespecified outcome classes are:
  improvement  : 2.5th percentile of dFC = FC0 - FC1 is > 0
  no_problem   : not improvement, and the 97.5th percentile of FC0 is < 0.01
  inconclusive : otherwise
"""

from __future__ import annotations

import argparse
import csv
import platform
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
STRUCTURES = ("E1", "E2", "E3", "E4", "E5", "E5'", "E6")
ROOT_SEED = 20261111
GRAPHS, REPEATS, DATASETS, BOOT = 100, 32, 200, 1000
DETECTION = (0.0, 0.5, 0.9)
ALARM = (0.05, 0.20)
STRESS = (1.0, 5.0)
FC_LIMIT = 0.01


def load(path):
    data = defaultdict(dict)
    for r in csv.DictReader(path.open(encoding="utf-8")):
        data[r["graph_id"]][r["structure"]] = (
            float(r["p_false_certification"]),
            float(r["p_certification"]),
            int(r["flipped"]),
        )
    ids = sorted(data)
    f = np.array([[data[g][s][0] for s in STRUCTURES] for g in ids])
    c = np.array([[data[g][s][1] for s in STRUCTURES] for g in ids])
    flip = np.array([[data[g][s][2] for s in STRUCTURES] for g in ids])
    return f, c, flip


def one_dataset(rng, f, c, flip, d, a, k):
    idx = rng.integers(0, f.shape[0], GRAPHS)
    f0 = np.minimum(f[idx] * k, c[idx])
    c0 = c[idx]
    alarm = np.where(flip[idx] == 1, d, a)
    r0_fc = rng.binomial(REPEATS, f0) / REPEATS
    r1_fc = rng.binomial(REPEATS, f0 * (1 - np.where(flip[idx] == 1, d, 0.0))) / REPEATS
    r0_cov = rng.binomial(REPEATS, c0) / REPEATS
    r1_cov = rng.binomial(REPEATS, c0 * (1 - alarm)) / REPEATS
    boot = rng.integers(0, GRAPHS, (BOOT, GRAPHS))
    fc0_b = r0_fc[boot].mean(axis=(1, 2))
    dfc_b = (r0_fc - r1_fc)[boot].mean(axis=(1, 2))
    dfc_lo = np.percentile(dfc_b, 2.5, method="inverted_cdf")
    fc0_hi = np.percentile(fc0_b, 97.5, method="inverted_cdf")
    outcome = (
        "improvement"
        if dfc_lo > 0
        else ("no_problem" if fc0_hi < FC_LIMIT else "inconclusive")
    )
    return {
        "fc0": r0_fc.mean(),
        "fc1": r1_fc.mean(),
        "dfc_lower": dfc_lo,
        "fc0_upper": fc0_hi,
        "coverage_loss": r0_cov.mean() - r1_cov.mean(),
        "outcome": outcome,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputs",
        type=Path,
        default=REPO / "experiments" / "power" / "decision_design_inputs_v5.csv",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=REPO / "experiments" / "power"
    )
    args = parser.parse_args()
    raw = args.output_dir / "power_analysis_raw_v5.csv"
    summary = args.output_dir / "power_analysis_summary_v5.csv"
    log = args.output_dir / "run_log_v5.txt"
    for p in (raw, summary, log):
        if p.exists():
            print(f"Refusing to overwrite existing output: {p}")
            return 1
    f, c, flip = load(args.inputs)
    rows = []
    for k in STRESS:
        for d in DETECTION:
            for a in ALARM:
                ss = np.random.SeedSequence(
                    [ROOT_SEED, 50, int(k * 10), int(d * 100), int(a * 100)]
                )
                rng = np.random.default_rng(ss)
                for i in range(DATASETS):
                    rows.append(
                        {
                            "stress": k,
                            "detection": d,
                            "alarm": a,
                            "dataset": i,
                            **one_dataset(rng, f, c, flip, d, a, k),
                        }
                    )
    with raw.open("x", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(
            {
                key: (repr(float(v)) if isinstance(v, (float, np.floating)) else v)
                for key, v in r.items()
            }
            for r in rows
        )
    groups = defaultdict(list)
    for r in rows:
        groups[(r["stress"], r["detection"], r["alarm"])].append(r)
    out = []
    for (k, d, a), g in groups.items():
        n = len(g)
        out.append(
            {
                "stress": k,
                "detection": d,
                "alarm": a,
                "datasets": n,
                "p_improvement": sum(x["outcome"] == "improvement" for x in g) / n,
                "p_no_problem": sum(x["outcome"] == "no_problem" for x in g) / n,
                "p_inconclusive": sum(x["outcome"] == "inconclusive" for x in g) / n,
                "mean_fc0": float(np.mean([x["fc0"] for x in g])),
                "mean_coverage_loss": float(np.mean([x["coverage_loss"] for x in g])),
            }
        )
    with summary.open("x", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    with log.open("x", encoding="utf-8", newline="\n") as h:
        h.write(
            f"Power analysis v5 (non-circular; split-99 design inputs)\ngraphs={GRAPHS} repeats={REPEATS} datasets={DATASETS} bootstrap={BOOT}\n"
        )
        h.write(
            f"python={sys.version.split()[0]}\nplatform={platform.platform()}\nnumpy={np.__version__}\n"
        )
    for r in out:
        print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
