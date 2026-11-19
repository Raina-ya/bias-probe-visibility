"""Simulation-only power check for the hardware readout pair-correlation test.

Planning only: split 99 (software tests and design checks), never reported as a
result.  No hardware, no IBM account.  Implements the statistics frozen in
docs/hardware/amendment_readout_v1.md, Sections 3-5, on synthetic 2x2 flip
tables.

Model.  For one qubit pair under preparation 00 (or 11), the assignment flips
(f_i, f_j) have marginals q_i = q_j = q and covariance c, so
P(11) = q^2 + c, P(10) = P(01) = q(1-q) - c, P(00) = (1-q)^2 - c.
The correlation coefficient is rho = c / (q(1-q)).

Two tests per pair-preparation, each with Holm over m = 2 * C(8, 2) = 56:
  detection  - two-sided Fisher exact test of independence (H0: c = 0);
  relevance  - one-sided parametric bootstrap of H0: c <= c*(q_i, q_j), where
               c* is the covariance above which the independent (tensored)
               readout model gives a larger error than no correction for the
               edge parity <Z_i Z_j> (amendment Section 2).
Power is the probability that the single affected pair-preparation is
rejected at the Holm first-step level alpha / m, which is the exact Holm
outcome when only one pair-preparation is affected and conservative otherwise.

Seeds: SeedSequence([ROOT_SEED, 99, 6, 5, 40, 8, 0, iq, irho, iS, test]) with
artifact 6 (shot draw), structure 5 (E5 family), probe 40 (P4a), width 8.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hw_stats_v1 import (  # noqa: E402
    c_max,
    c_star,
    estimates,
    fisher_two_sided,
    joint,
    r_ind,
    relevance_p,
    relevance_stat,
)

OUTPUTS = ("readout_power_v1.csv", "readout_power_v1.json")
__all__ = ["c_max", "c_star", "estimates", "fisher_two_sided", "joint", "r_ind",
           "relevance_p", "relevance_stat"]
ROOT_SEED = 20261111
SPLIT = 99
ALPHA = 0.05
WIDTH = 8
M_TESTS = 2 * math.comb(WIDTH, 2)  # 56 pair-preparations (P4a: preps 00 and 11)
LEVEL = ALPHA / M_TESTS

Q_GRID = (0.005, 0.01, 0.02, 0.05)
RHO_GRID = (0.0, 0.02, 0.05, 0.10, 0.20)
S_GRID = (100, 300, 1000, 3000, 10000, 30000)
RELEVANCE_EFFECTS = (1.0, 1.5)  # c / c*: size check at the boundary, power at 1.5 c*


def stream(iq: int, irho: int, i_s: int, test: int) -> np.random.Generator:
    return np.random.default_rng(
        np.random.SeedSequence(
            [ROOT_SEED, SPLIT, 6, 5, 40, WIDTH, 0, iq, irho, i_s, test]
        )
    )


def run(reps: int, boot: int) -> list[dict]:
    rows = []
    for iq, q in enumerate(Q_GRID):
        base = q * (1 - q)
        for i_s, s in enumerate(S_GRID):
            for irho, rho in enumerate(RHO_GRID):
                rng = stream(iq, irho, i_s, 0)
                tables = rng.multinomial(s, joint(q, q, rho * base), size=reps)
                rej = sum(fisher_two_sided(*map(int, t)) <= LEVEL for t in tables)
                rows.append(
                    {"test": "detection", "q": q, "shots": s, "rho": rho,
                     "c_over_cstar": rho * base / c_star(q, q),
                     "reps": reps, "rejections": int(rej), "power": rej / reps}
                )
            for ie, eff in enumerate(RELEVANCE_EFFECTS):
                c = eff * c_star(q, q)
                rng = stream(iq, 100 + ie, i_s, 1)
                tables = rng.multinomial(s, joint(q, q, c), size=reps)
                rej = sum(relevance_p(t, rng, boot) <= LEVEL for t in tables)
                rows.append(
                    {"test": "relevance", "q": q, "shots": s, "rho": c / base,
                     "c_over_cstar": eff, "reps": reps, "rejections": int(rej),
                     "power": rej / reps}
                )
    return rows


def min_shots(rows: list[dict], test: str, q: float, key: str, value: float,
              target: float = 0.8) -> int | None:
    ok = [r["shots"] for r in rows if r["test"] == test and r["q"] == q
          and abs(r[key] - value) < 1e-12 and r["power"] >= target]
    return min(ok) if ok else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--boot", type=int, default=1999)
    ap.add_argument("--out", type=Path, default=Path("experiments/hardware"))
    args = ap.parse_args(argv)
    started = time.perf_counter()
    rows = run(args.reps, args.boot)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "readout_power_v1.csv").open("w", newline="\n", encoding="utf-8") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})
    summary = {
        "split": SPLIT, "purpose": "planning only; never a result",
        "width": WIDTH, "m_tests": M_TESTS, "level": LEVEL,
        "reps": args.reps, "boot": args.boot,
        "c_star": {str(q): c_star(q, q) for q in Q_GRID},
        "rho_star": {str(q): c_star(q, q) / (q * (1 - q)) for q in Q_GRID},
        "min_shots_power_0.8": {
            str(q): {
                **{f"detection_rho_{rho}": min_shots(rows, "detection", q, "rho", rho)
                   for rho in RHO_GRID if rho > 0},
                "relevance_1.5cstar": min_shots(rows, "relevance", q, "c_over_cstar", 1.5),
            }
            for q in Q_GRID
        },
        "max_false_rejection": {
            "detection_rho_0": max(r["power"] for r in rows
                                   if r["test"] == "detection" and r["rho"] == 0),
            "relevance_at_cstar": max(r["power"] for r in rows
                                      if r["test"] == "relevance" and r["c_over_cstar"] == 1.0),
        },
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__,
                        "platform": platform.platform()},
        "seconds": round(time.perf_counter() - started, 1),
    }
    (args.out / "readout_power_v1.json").write_text(
        json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary["min_shots_power_0.8"], indent=1))
    print(json.dumps(summary["max_false_rejection"]), summary["seconds"], "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
