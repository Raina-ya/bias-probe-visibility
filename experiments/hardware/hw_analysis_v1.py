"""Analysis of the hardware readout amendment v1 (Sections 3 and 4).

Reads only immutable raw records of the main stage (the pilot is excluded),
checks the record index, sums counts per circuit over jobs, converts Qiskit
keys to the internal bit order, and for each of the 2 x 28 pair-preparations
computes: flip table, plug-in estimates, relevance test (one-sided parametric
bootstrap, B = 9,999), detection test (two-sided Fisher exact), Holm over the
56 tests per family, and a 95% percentile bootstrap interval for c.

H-R1 (registered prediction): no pair-preparation rejects the relevance null.

Seeds: SeedSequence([20261111, split, 7, 5, 40, 8, 0, pair_index, preparation,
0, test]) with split 60 for the real run and 99 for dry runs; test 0 is the
relevance bootstrap, 1 the interval.  The output depends only on the raw
records and these seeds, so it is recomputable.
"""

from __future__ import annotations

import argparse
import itertools
import json
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hw_circuits_v1 as hc  # noqa: E402
import hw_rawio_v1 as rio  # noqa: E402
import hw_stats_v1 as st  # noqa: E402

OUTPUTS = ("analysis_v1.json", "analysis_v1.md")
ROOT_SEED = 20261111
BOOT = 9999
REAL_SPLIT = 60
DRY_SPLIT = 99


def pairs(width: int = hc.WIDTH) -> list[tuple[int, int]]:
    return list(itertools.combinations(range(width), 2))


def seed(split: int, pair_index: int, preparation: int, test: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence(
        [ROOT_SEED, split, 7, 5, 40, hc.WIDTH, 0, pair_index, preparation, 0, test]))


def main_counts(run_dir: Path) -> tuple[dict[str, dict[str, int]], list[dict]]:
    problems = rio.verify_index(run_dir)
    if problems:
        raise ValueError("record index problems: " + "; ".join(problems))
    if not (run_dir / "markers" / "main.success").is_file():
        raise ValueError("main stage has not succeeded")
    jobs = sorted((run_dir / "raw").glob("main_job*.json"))
    jobs = [p for p in jobs if not p.name.endswith("_failed.json")]
    if not jobs:
        raise ValueError("no main-stage raw records")
    totals: dict[str, dict[str, int]] = {c: {} for c in hc.CIRCUITS}
    meta = []
    for path in jobs:
        rec = json.loads(path.read_text(encoding="utf-8"))
        meta.append({"job_id": rec["job_id"], "shots_per_circuit": rec["shots_per_circuit"],
                     "usage_seconds": rec["usage_seconds"]})
        for circuit, counts in rec["counts"].items():
            for z, n in hc.internal_counts(counts).items():
                totals[circuit][z] = totals[circuit].get(z, 0) + n
    return totals, meta


def analyse(totals: dict[str, dict[str, int]], split: int, boot: int = BOOT) -> dict:
    rows = []
    for prep_index, circuit in enumerate(hc.CIRCUITS):
        for pair_index, (i, j) in enumerate(pairs()):
            table = np.array(hc.pair_table(totals[circuit], circuit, i, j))
            qi, qj, c = (float(x[0]) for x in st.estimates(table[None, :] * 1.0))
            zero_margin = min(qi, qj) == 0.0
            cs = st.c_star(qi, qj)
            p_rel = 1.0 if zero_margin else st.relevance_p(
                table, seed(split, pair_index, prep_index, 0), boot)
            p_det = st.fisher_two_sided(*map(int, table))
            lo, hi = st.covariance_interval(table, seed(split, pair_index, prep_index, 1), boot)
            denom = (qi * (1 - qi) * qj * (1 - qj)) ** 0.5
            rows.append({
                "circuit": circuit, "pair": [i, j], "table": table.tolist(),
                "q_i": qi, "q_j": qj, "c_hat": c, "c_star": cs,
                "c_over_cstar": c / cs if cs > 0 else None,
                "rho_hat": c / denom if denom > 0 else None,
                "c_interval_95": [lo, hi], "p_relevance": p_rel, "p_detection": p_det,
                "relevance_uninformative": zero_margin,
            })
    rel_reject, rel_adj = st.holm([r["p_relevance"] for r in rows])
    det_reject, det_adj = st.holm([r["p_detection"] for r in rows])
    for r, a, b, c, d in zip(rows, rel_reject, rel_adj, det_reject, det_adj, strict=True):
        r.update({"relevance_reject": a, "relevance_p_holm": b,
                  "detection_reject": c, "detection_p_holm": d})
    marginals = {}
    for circuit in hc.CIRCUITS:
        n = sum(totals[circuit].values())
        marginals[circuit] = [
            sum(m for z, m in totals[circuit].items() if hc.flip_pattern(z, circuit)[k] == "1") / n
            for k in range(hc.WIDTH)]
    upper = max(r["c_interval_95"][1] for r in rows)
    return {
        "split": split, "bootstrap": boot, "m_tests_per_family": len(rows),
        "shots_per_circuit": {c: sum(totals[c].values()) for c in hc.CIRCUITS},
        "flip_rates_per_logical_qubit": marginals,
        "relevance_rejections": int(sum(rel_reject)),
        "detection_rejections": int(sum(det_reject)),
        "H_R1": "supported (no relevance rejection)" if not any(rel_reject)
                else "falsified (at least one relevance rejection)",
        "max_c_upper_95": upper,
        "median_rho_hat": statistics.median(r["rho_hat"] for r in rows if r["rho_hat"] is not None),
        "pairs": rows,
    }


def report(result: dict, meta: list[dict], dry_run: bool) -> str:
    lines = [
        "# Hardware readout amendment v1: analysis" + (" (DRY RUN, synthetic counts)" if dry_run else ""),
        "",
        "Evidence type: " + ("offline dry run on synthetic counts; not a result." if dry_run
                             else "hardware-derived; exploratory with respect to protocol v4 endpoints."),
        "",
        f"**H-R1: {result['H_R1']}.** Relevance rejections: {result['relevance_rejections']} of "
        f"{result['m_tests_per_family']} (Holm, alpha 0.05). Detection rejections: "
        f"{result['detection_rejections']} of {result['m_tests_per_family']}.",
        "",
        f"Shots per circuit: {result['shots_per_circuit']}. Main jobs: {len(meta)}. "
        f"Largest 95% upper bound on c over pair-preparations: {result['max_c_upper_95']:.6f}.",
        "",
        "| Circuit | Pair | c_hat | c* | rho_hat | p_rel (Holm) | p_det (Holm) |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in result["pairs"]:
        rho = "n/a" if r["rho_hat"] is None else f"{r['rho_hat']:.4f}"
        lines.append(f"| {r['circuit']} | {r['pair'][0]}-{r['pair'][1]} | {r['c_hat']:.6f} | "
                     f"{r['c_star']:.6f} | {rho} | {r['relevance_p_holm']:.4g} | "
                     f"{r['detection_p_holm']:.4g} |")
    return "\n".join(lines) + "\n"


def run(run_dir: Path, out_dir: Path, dry_run: bool, boot: int = BOOT) -> dict:
    totals, meta = main_counts(run_dir)
    result = analyse(totals, DRY_SPLIT if dry_run else REAL_SPLIT, boot)
    result["dry_run"] = dry_run
    result["main_jobs"] = meta
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / OUTPUTS[0]).open("x", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    with (out_dir / OUTPUTS[1]).open("x", encoding="utf-8", newline="\n") as h:
        h.write(report(result, meta, dry_run))
    return result


def cli(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Analyse the hardware readout run (main stage only).")
    ap.add_argument("--run-dir", type=Path, default=Path("results/hardware_v1"))
    # Outside the run folder, whose record index must list only runner records.
    ap.add_argument("--out", type=Path, default=Path("results/hardware_v1_analysis"))
    args = ap.parse_args(argv)
    result = run(args.run_dir, args.out, dry_run=False)
    print(result["H_R1"], result["relevance_rejections"], result["detection_rejections"])
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
