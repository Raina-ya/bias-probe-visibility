"""Task 3-1: primary endpoint of protocol v4 on the holdout, computed once.

Section 11.1.  For each non-null structure s at its main operating point:

* R0 (P0 rows, all N shots on the targets): certify when L_T > 0
  (``alarm_p0`` is False); the winner is the sign of the sample gap.
* R1 (rows of the designated probe j(s) at f = 0.10): certify when the row's
  own L_T > 0 and the j(s) cell component does not exceed its clean-E0
  threshold (alpha 0.05, same width-depth stratum, strict alarm T > tau).
* A certification is false when its winner differs from the ideal winner; a
  certified ideal tie is false.  Scoring uses the reference file written after
  the run finalized.

dFC = (1/7) sum_s [FC_s(R0) - FC_s(R1)], 95% interval from 10,000 stratified
graph-cluster bootstrap resamples with indices shared across structures and
rules (analysis_v4.primary_decision), seed
SeedSequence([ROOT_SEED, 20, 7, 0, ...]).  Outcome: improvement if the 2.5th
percentile of dFC > 0; no decision problem if not and the 97.5th percentile of
pooled FC(R0) < 0.01; otherwise inconclusive.  The no-problem bound is also
reported at 0.005 and 0.02 (Section 8) with the same resamples; these never
replace the main outcome.

Missing data rule, fixed before the run: if any unit needed here failed or is
absent, the primary outcome is ``not_evaluable`` and a complete-case analysis
is reported as a labelled sensitivity result.

Inputs are checked first: the confirmatory lock and its registration, the
single-run marker, the thresholds file hash recorded in the lock.  Outputs are
written once: results/holdout_v4/primary_endpoint_v4.json and
docs/results/primary_endpoint_v4.md.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import analysis_v4  # noqa: E402
import cells_v4  # noqa: E402
import split_guard_v4  # noqa: E402
from hashing import canonical_sha256  # noqa: E402
from protocol_contract import ROOT_SEED  # noqa: E402

OUT = REPO / "results" / "holdout_v4"
REPORT = REPO / "docs" / "results" / "primary_endpoint_v4.md"
THRESHOLDS = Path("results/development_v4/thresholds_v4.csv")
SENSITIVITY_BOUNDS = (0.005, 0.02)
BOOTSTRAP_KEY = [ROOT_SEED, 20, 7, 0, 0, 0, 0, 0, 0, 0, 0]


def width_depth(graph_id: str) -> tuple[int, int]:
    parts = graph_id.split("-")
    return int(parts[-3][1:]), int(parts[-2][1:])


def graph_order(graph_id: str) -> tuple[int, int, int]:
    parts = graph_id.split("-")
    return int(parts[-3][1:]), int(parts[-2][1:]), int(parts[-1][1:])


def check_inputs(repo: Path) -> None:
    split_guard_v4.require_confirmatory_lock(repo)
    if not split_guard_v4.marker_path(repo, "holdout").is_file():
        raise SystemExit("refused: the holdout has not finalized (no marker)")
    lock = json.loads(
        (repo / split_guard_v4.CONFIRMATORY_LOCK).read_text(encoding="utf-8")
    )
    product = lock["products"]["thresholds_csv"]
    if (
        product["path"] != THRESHOLDS.as_posix()
        or canonical_sha256(repo / THRESHOLDS) != product["sha256"]
    ):
        raise SystemExit("refused: thresholds differ from the confirmatory lock")


def clean_e0_taus(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as h:
        return {
            (r["probe"], r["structure"], int(r["width"]), int(r["depth"])): float(
                r["tau"]
            )
            for r in csv.DictReader(h)
            if r["null"] == "clean_e0" and r["alpha"] == "0.05"
        }


def ideal_winners(path: Path) -> dict[str, int]:
    out = {}
    with path.open(encoding="utf-8", newline="") as h:
        for r in csv.DictReader(h):
            if r["structure"] != "E1" or r["point"] != "main":
                continue  # the ideal gap does not depend on the structure
            gap = float(r["ideal_gap"])
            out[r["graph_id"]] = 0 if r["ideal_tie"] == "1" else (1 if gap > 0 else -1)
    return out


def load_main_rows(out: Path, needed: set[tuple[str, str]]):
    """{(probe, structure): {graph_id: [row by repeat]}} and failed units."""

    rows, failed = defaultdict(dict), []
    for path in sorted((out / "main").glob("*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                entry = json.loads(line)
                _, probe, structure, _, _, graph_id = entry["unit"]
                if (probe, structure) not in needed:
                    continue
                if entry["status"] != "ok":
                    failed.append(entry["unit"])
                    continue
                ordered = sorted(entry["rows"], key=lambda r: r["repeat"])
                if any(r["split"] != "holdout" for r in ordered):
                    raise SystemExit("refused: non-holdout row in holdout shards")
                rows[(probe, structure)][graph_id] = ordered
    return rows, failed


def decisions(unit_rows, graphs, probe, structure, taus, use_probe):
    """certified, winner arrays (graphs x repeats); NaN-free; None if incomplete."""

    if any(g not in unit_rows for g in graphs):
        return None
    certified, winner = [], []
    for g in graphs:
        w, d = width_depth(g)
        c_row, w_row = [], []
        for row in unit_rows[g]:
            ok = not row["alarm_p0"]
            if use_probe:
                merged = {"statistic": row["statistic"], **row["components"]}
                value = merged.get(cells_v4.component(probe, structure))
                if value is None:
                    raise SystemExit(f"missing component for {probe}/{structure}")
                ok = ok and not (float(value) > taus[(probe, structure, w, d)])
            gap = row["components"]["gap_target"]
            c_row.append(ok)
            w_row.append(1 if gap > 0 else (-1 if gap < 0 else 0))
        certified.append(c_row)
        winner.append(w_row)
    return np.array(certified, dtype=bool), np.array(winner, dtype=int)


def rule_arrays(rows, graphs, ideal, taus, probe_for):
    fc0, fc1, c0, c1 = {}, {}, {}, {}
    for s in cells_v4.STRUCTURES:
        r0 = decisions(rows[("P0", s)], graphs, "P0", s, taus, use_probe=False)
        r1 = decisions(
            rows[(probe_for(s), s)], graphs, probe_for(s), s, taus, use_probe=True
        )
        if r0 is None or r1 is None:
            return None
        fc0[s] = analysis_v4.false_certification(r0[0], r0[1], ideal)
        fc1[s] = analysis_v4.false_certification(r1[0], r1[1], ideal)
        c0[s], c1[s] = r0[0], r1[0]
    return fc0, fc1, c0, c1


def evaluate(rows, graphs, ideal, taus, probe_for, strata):
    arrays = rule_arrays(rows, graphs, ideal, taus, probe_for)
    if arrays is None:
        return None
    fc0, fc1, c0, c1 = arrays
    results = {}
    for bound in (analysis_v4.NO_PROBLEM_BOUND, *SENSITIVITY_BOUNDS):
        rng = np.random.default_rng(np.random.SeedSequence(BOOTSTRAP_KEY))
        results[bound] = analysis_v4.primary_decision(
            fc0, fc1, c0, c1, strata, rng, no_problem_bound=bound
        )
    per = {
        s: {
            "FC_R0": float(fc0[s].mean()),
            "FC_R1": float(fc1[s].mean()),
            "C_R0": float(c0[s].mean()),
            "C_R1": float(c1[s].mean()),
            "R0_false_certifications": int(fc0[s].sum()),
            "R1_false_certifications": int(fc1[s].sum()),
            "R0_false_cert_graphs": int(fc0[s].any(axis=1).sum()),
            "intercepted": analysis_v4.interception(fc0[s], c1[s])[0],
            "interception_units": analysis_v4.interception(fc0[s], c1[s])[1],
        }
        for s in cells_v4.STRUCTURES
    }
    return results, per


def summary(result) -> dict:
    return {
        "dFC": result.dfc,
        "dFC_lower_2.5": result.dfc_lower,
        "dFC_upper_97.5": result.dfc_upper,
        "dFC_lower_minus_0": result.dfc_lower,
        "FC_R0_pooled": result.fc0,
        "FC_R0_upper_97.5": result.fc0_upper,
        "coverage_loss_pooled": result.coverage_loss,
        "outcome": result.outcome,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--skip-input-check", action="store_true", help="tests only")
    args = parser.parse_args(argv)
    if not args.skip_input_check:
        check_inputs(REPO)
    taus = clean_e0_taus(REPO / THRESHOLDS)
    ideal_map = ideal_winners(args.out / "reference" / "holdout_reference_v4.csv")
    graphs = sorted(ideal_map, key=graph_order)
    strata = [width_depth(g) for g in graphs]
    ideal = np.array([ideal_map[g] for g in graphs])
    needed = {("P0", s) for s in cells_v4.STRUCTURES}
    needed |= {(cells_v4.DESIGNATED[s], s) for s in cells_v4.STRUCTURES}
    needed |= {("P2", s) for s in cells_v4.STRUCTURES}
    rows, failed = load_main_rows(args.out, needed)

    report = {
        "graphs": len(graphs),
        "repeats": 32,
        "failed_units": [list(u) for u in failed],
        "ideal_ties": int((ideal == 0).sum()),
        "bootstrap_seed_key": BOOTSTRAP_KEY,
        "inputs": {
            "thresholds_sha256": canonical_sha256(REPO / THRESHOLDS),
            "reference_sha256": canonical_sha256(
                args.out / "reference" / "holdout_reference_v4.csv"
            ),
            "main_shards": {
                p.name: canonical_sha256(p)
                for p in sorted((args.out / "main").glob("*.jsonl.gz"))
            },
        },
    }
    variants = {
        "primary_designated": lambda s: cells_v4.DESIGNATED[s],
        "secondary_structure_agnostic_P2": lambda s: "P2",
    }
    for name, probe_for in variants.items():
        complete = evaluate(rows, graphs, ideal, taus, probe_for, strata)
        if complete is not None and not failed:
            results, per = complete
            report[name] = {
                "main": summary(results[analysis_v4.NO_PROBLEM_BOUND]),
                "no_problem_bound_sensitivity": {
                    str(b): summary(results[b])["outcome"] for b in SENSITIVITY_BOUNDS
                },
                "per_structure": per,
            }
            continue
        # Missing-data rule: not evaluable; complete-case analysis as sensitivity.
        keep = [
            k
            for k, g in enumerate(graphs)
            if all(
                g in rows[(p, s)]
                for s in cells_v4.STRUCTURES
                for p in ("P0", probe_for(s))
            )
        ]
        entry = {
            "outcome": "not_evaluable",
            "reason": "missing or failed units",
            "complete_case_graphs": len(keep),
        }
        cc_strata = [strata[k] for k in keep]
        if keep and set(cc_strata) == set(strata):
            cc = evaluate(
                rows, [graphs[k] for k in keep], ideal[keep], taus, probe_for, cc_strata
            )
            if cc is not None:
                entry["complete_case_sensitivity"] = summary(
                    cc[0][analysis_v4.NO_PROBLEM_BOUND]
                )
        report[name] = entry

    json_path = args.out / "primary_endpoint_v4.json"
    with json_path.open("x", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8", newline="\n") as h:
        h.write(render(report, json_path))
    print(
        json.dumps(
            {
                "outcome": report["primary_designated"]
                .get("main", report["primary_designated"])
                .get("outcome"),
                "json_sha256": canonical_sha256(json_path),
            }
        )
    )
    return 0


def render(report: dict, json_path: Path) -> str:
    p = report["primary_designated"]
    lines = [
        "# Primary endpoint, protocol v4 holdout (Task 3-1)",
        "",
        "Evidence type: noisy simulation, holdout split 20, read once. Rule:",
        "protocol v4 Section 11.1, thresholds and operating points from the",
        "confirmatory lock (OSF j597k). Recomputable from the raw rows with",
        "`experiments/holdout/score_primary_v4.py`.",
        "",
        f"Graphs: {report['graphs']}; repeats: {report['repeats']}; ideal ties: "
        f"{report['ideal_ties']}; failed units: {len(report['failed_units'])}.",
        "",
    ]
    if "main" not in p:
        lines += [f"**Outcome: {p['outcome']}** ({p['reason']}).", ""]
        return "\n".join(lines)
    m = p["main"]
    lines += [
        f"**Outcome: {m['outcome']}.**",
        "",
        "| Quantity | Value | Threshold | Value - threshold |",
        "|---|---:|---:|---:|",
        f"| dFC (point) | {m['dFC']:+.6f} | | |",
        f"| dFC 2.5th percentile | {m['dFC_lower_2.5']:+.6f} | 0 (improvement if >) | {m['dFC_lower_2.5']:+.6f} |",
        f"| dFC 97.5th percentile | {m['dFC_upper_97.5']:+.6f} | | |",
        f"| Pooled FC(R0) | {m['FC_R0_pooled']:.6f} | | |",
        f"| Pooled FC(R0) 97.5th percentile | {m['FC_R0_upper_97.5']:.6f} | 0.01 (no problem if <) | {m['FC_R0_upper_97.5'] - 0.01:+.6f} |",
        f"| Pooled coverage loss C(R0)-C(R1) | {m['coverage_loss_pooled']:+.6f} | | |",
        "",
        "No-problem bound sensitivity (Section 8; never replaces the main outcome): "
        + ", ".join(f"{b}: {o}" for b, o in p["no_problem_bound_sensitivity"].items())
        + ".",
        "",
        "## Per structure (main operating point)",
        "",
        "| Structure | Probe | FC(R0) | FC(R1) | C(R0) | C(R1) | R0 false certs | R0 false-cert graphs | Interception (units) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for s, v in p["per_structure"].items():
        inter = (
            "insufficient"
            if v["intercepted"] != v["intercepted"]
            else f"{v['intercepted']:.3f}"
        )
        lines.append(
            f"| {s} | {cells_v4.DESIGNATED[s]} | {v['FC_R0']:.6f} | {v['FC_R1']:.6f} | "
            f"{v['C_R0']:.4f} | {v['C_R1']:.4f} | {v['R0_false_certifications']} | "
            f"{v['R0_false_cert_graphs']} | {inter} ({v['interception_units']}) |"
        )
    q = report["secondary_structure_agnostic_P2"]
    lines += [
        "",
        "## Secondary: structure-agnostic variant (P2 for every structure)",
        "",
    ]
    if "main" in q:
        lines.append(
            f"Outcome {q['main']['outcome']}; dFC {q['main']['dFC']:+.6f} "
            f"[{q['main']['dFC_lower_2.5']:+.6f}, {q['main']['dFC_upper_97.5']:+.6f}]; "
            f"coverage loss {q['main']['coverage_loss_pooled']:+.6f}. Secondary endpoint."
        )
    else:
        lines.append(f"{q['outcome']} ({q['reason']}).")
    lines += ["", f"Machine-readable result: `{json_path.name}`.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
