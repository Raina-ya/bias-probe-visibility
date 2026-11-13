"""Task 2-3: alarm thresholds and development mismatch report, protocol v4.

Inputs: the development raw shards written by run_development_v4.py (split 10
only).  Outputs (each written once, never overwritten):

  results/development_v4/thresholds_v4.csv   machine-readable thresholds
  docs/freeze/thresholds_v4.md               the same thresholds, reviewed form
  docs/freeze/dev_mismatch_v4.md             development labels vs the matrix

Rules applied, all frozen in protocol v4 and not chosen here:

* Section 6.3: within each probe, cell component, width-depth stratum and
  calibration null, tau is the order statistic of rank
  min(n, ceil((n+1)(1-alpha))) (exact rational rank, alarm_calibration.py);
  the alarm is strict, T > tau; a null whose component is identically 0 gives
  tau = 0 and is reported.
* Visibility cells use their matched null (cells_v4.MATCHED_NULL); decision
  endpoints use clean E0 with all seven common-mode offsets.
* Section 8 / v3 labelling rule (analysis.classify): visible if power >= 0.80
  and matched-null false alarm <= 0.10; blind if power <= 0.10; else partial.
  Every comparison reports value - threshold.

Development labels are descriptive.  Protocol v4 Section 16.3: a disagreement
is a failed prediction and never revises the matrix, a probe, or a threshold.
Section 5.2: an invariant-stratum disagreement indicates an implementation or
derivation error; p5_e1_diagnostic_v4.py investigates the one observed in
the v4 development run (P5/E1).

E0 rows carry no temporal blocks, so the E6-only component
``temporal_contrast`` is not recorded for them (execution contract v4, item 2).
Its clean-E0 null is therefore identically 0 and receives tau = 0 under the
degenerate-null rule; each such entry is flagged ``not_recorded_in_e0``.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import alarm_calibration  # noqa: E402
import analysis  # noqa: E402
import cells_v4  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

OUT = REPO / "results" / "development_v4"
THRESHOLDS_CSV = OUT / "thresholds_v4.csv"
THRESHOLDS_MD = REPO / "docs" / "freeze" / "thresholds_v4.md"
MISMATCH_MD = REPO / "docs" / "freeze" / "dev_mismatch_v4.md"
ALPHAS = ("0.05", "0.01", "0.10")
# Section 8 sensitivity: blind boundary paired with each alpha.
BLIND_FOR_ALPHA = {"0.05": 0.10, "0.01": 0.06, "0.10": 0.15}


def width_depth(graph_id: str) -> tuple[int, int]:
    parts = graph_id.split("-")
    return int(parts[-3][1:]), int(parts[-2][1:])


def load(shards):
    """Return {(phase, probe, structure, setting): [(stratum, graph, repeat, row)]}."""

    data = defaultdict(list)
    splits = set()
    for path in shards:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                unit = json.loads(line)
                if unit["status"] != "ok":
                    raise ValueError(f"failed unit in {path}: {unit['unit']}")
                phase, probe, structure, setting, _, graph_id = unit["unit"]
                for row in unit["rows"]:
                    splits.add(row["split"])
                    data[(phase, probe, structure, setting)].append(
                        (
                            width_depth(graph_id),
                            graph_id,
                            row["repeat"],
                            {"statistic": row["statistic"], **row["components"]},
                        )
                    )
    if splits != {"development"}:
        raise ValueError(
            f"rows from splits {sorted(splits)}; expected development only"
        )
    return data


def value(row: dict, probe: str, structure: str):
    return row.get(cells_v4.component(probe, structure))


def thresholds_for(entries, probe, structure):
    """Per-stratum thresholds for one null; returns (rows, notes)."""

    by_stratum = defaultdict(list)
    missing = 0
    for stratum, _, _, row in entries:
        v = value(row, probe, structure)
        if v is None:
            missing += 1
        else:
            by_stratum[stratum].append(float(v))
    out = {}
    if missing and not by_stratum:
        for stratum in sorted({e[0] for e in entries}):
            n = sum(1 for e in entries if e[0] == stratum)
            out[stratum] = {a: (0.0, n, True, "not_recorded_in_e0") for a in ALPHAS}
        return out
    if missing:
        raise ValueError(f"component partly missing for {probe}/{structure}")
    for stratum, scores in sorted(by_stratum.items()):
        degenerate = all(s == 0.0 for s in scores)
        out[stratum] = {
            a: (
                alarm_calibration.threshold(scores, a),
                len(scores),
                degenerate,
                "degenerate" if degenerate else "",
            )
            for a in ALPHAS
        }
    return out


def calibrate(data):
    rows = []
    for probe, structure in cells_v4.cells():
        component = cells_v4.component(probe, structure)
        nulls = {
            "matched": data[
                ("nulls", probe, structure, cells_v4.MATCHED_NULL[structure])
            ],
            "clean_e0": [
                e
                for (ph, p, s, _), v in data.items()
                if ph == "nulls" and p == probe and s == "E0"
                for e in v
            ],
        }
        for kind, entries in nulls.items():
            for stratum, per_alpha in thresholds_for(entries, probe, structure).items():
                for alpha, (tau, n, degenerate, note) in per_alpha.items():
                    rows.append(
                        {
                            "null": kind,
                            "probe": probe,
                            "structure": structure,
                            "component": component,
                            "width": stratum[0],
                            "depth": stratum[1],
                            "alpha": alpha,
                            "rank": alarm_calibration.order_rank(n, alpha),
                            "n": n,
                            "tau": repr(tau),
                            "degenerate": int(degenerate),
                            "note": note,
                        }
                    )
    return rows


def tau_map(rows, kind, alpha):
    return {
        (r["probe"], r["structure"], (r["width"], r["depth"])): float(r["tau"])
        for r in rows
        if r["null"] == kind and r["alpha"] == alpha
    }


def alarm_rate(entries, probe, structure, taus):
    hits = [
        float(value(row, probe, structure)) > taus[(probe, structure, st)]
        for st, _, _, row in entries
    ]
    return sum(hits) / len(hits), len(hits)


def visibility(data, rows, chosen):
    """Development power and matched-null false alarm for each of the 42 cells."""

    results = {}
    for alpha in ALPHAS:
        taus = tau_map(rows, "matched", alpha)
        for probe, structure in cells_v4.cells():
            main = data[("main", probe, structure, chosen[structure])]
            null = data[("nulls", probe, structure, cells_v4.MATCHED_NULL[structure])]

            power, n_main = alarm_rate(main, probe, structure, taus)
            false_alarm, n_null = alarm_rate(null, probe, structure, taus)
            results[(alpha, probe, structure)] = (power, false_alarm, n_main, n_null)
    return results


def label(power, false_alarm, power_visible=0.80, false_alarm_visible=0.10, blind=0.10):
    return analysis.classify(
        power,
        false_alarm,
        analysis.Thresholds(power_visible, false_alarm_visible, blind),
    )


def read_chosen(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {
            r["structure"]: r["setting"]
            for r in csv.DictReader(handle)
            if r["chosen"] == "1" and r["point"] == "main"
        }


def write_outputs(rows, vis, chosen, shards, out_csv, thresholds_md, mismatch_md):
    matrix = cells_v4.load_matrix()
    fields = list(rows[0])
    shard_hashes = {
        p.relative_to(REPO).as_posix()
        if p.is_relative_to(REPO)
        else p.name: canonical_sha256(p)
        for p in shards
    }
    with out_csv.open("x", encoding="utf-8", newline="\n") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    main = [r for r in rows if r["alpha"] == "0.05"]
    lines = [
        "# Alarm thresholds, protocol v4 (Task 2-3)",
        "",
        "Evidence type: noisy simulation, development split 10 only. Rule: protocol",
        "v4 Section 6.3, main alpha 0.05 (sensitivity alphas 0.01 and 0.10 are in",
        f"`{out_csv.relative_to(REPO).as_posix() if out_csv.is_relative_to(REPO) else out_csv.name}`).",
        "Each threshold is a per-stratum order statistic of n development null",
        "scores; the alarm is strict, `T > tau`. Thresholds were computed once and",
        "are not recalibrated on non-null settings or holdout data.",
        "",
        f"- Threshold rows (all alphas): {len(rows)}; main-alpha rows: {len(main)}.",
        f"- Matched-null rows with a degenerate (identically 0) null: "
        f"{sum(1 for r in main if r['null'] == 'matched' and r['degenerate'])} of "
        f"{sum(1 for r in main if r['null'] == 'matched')}.",
        f"- Clean-E0 rows with a degenerate null: "
        f"{sum(1 for r in main if r['null'] == 'clean_e0' and r['degenerate'])} of "
        f"{sum(1 for r in main if r['null'] == 'clean_e0')}, of which "
        f"{sum(1 for r in main if r['note'] == 'not_recorded_in_e0')} are "
        "`temporal_contrast` (not recorded under E0; tau = 0).",
        "",
        "## Decision-endpoint thresholds (clean E0, alpha 0.05)",
        "",
        "Designated probes (E1 P1, E2 P2, E3 P3, E4--E6 P4a) and the",
        "structure-agnostic P2 variant. Range over the 25 width-depth strata.",
        "",
        "| Structure | Probe | Component | n per stratum | min tau | max tau | degenerate strata |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for structure in cells_v4.STRUCTURES:
        for probe in sorted({cells_v4.DESIGNATED[structure], "P2"}):
            sel = [
                r
                for r in main
                if r["null"] == "clean_e0"
                and r["probe"] == probe
                and r["structure"] == structure
            ]
            taus = [float(r["tau"]) for r in sel]
            lines.append(
                f"| {structure} | {probe} | {sel[0]['component']} | {sel[0]['n']} | "
                f"{min(taus):.6g} | {max(taus):.6g} | {sum(r['degenerate'] for r in sel)} |"
            )
    lines += [
        "",
        "## Matched-null thresholds (alpha 0.05)",
        "",
        "Range over the 25 width-depth strata for each of the 42 cells.",
        "",
        "| Probe | Structure | Component | Matched null | n per stratum | min tau | max tau | degenerate strata |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for probe, structure in cells_v4.cells():
        sel = [
            r
            for r in main
            if r["null"] == "matched"
            and r["probe"] == probe
            and r["structure"] == structure
        ]
        taus = [float(r["tau"]) for r in sel]
        lines.append(
            f"| {probe} | {structure} | {sel[0]['component']} | "
            f"`{cells_v4.MATCHED_NULL[structure]}` | {sel[0]['n']} | {min(taus):.6g} | "
            f"{max(taus):.6g} | {sum(r['degenerate'] for r in sel)} |"
        )
    lines += ["", "## Inputs (SHA-256)", ""]
    lines += [f"- `{k}`: `{v}`" for k, v in sorted(shard_hashes.items())]
    lines += [f"- `{out_csv.name}`: `{canonical_sha256(out_csv)}`", ""]
    with thresholds_md.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))

    # ------------------------------------------------------------ mismatch
    m = [
        "# Development mismatch report, protocol v4 (Task 2-3)",
        "",
        "Evidence type: noisy simulation, development split 10 only (50 graphs, two",
        "per width-depth stratum, 32 repeats). These labels are descriptive. Under",
        "protocol v4 Section 16.3 a disagreement is a failed prediction and does not",
        "revise the matrix, a probe, a threshold, or a tolerance. An",
        "invariant-stratum disagreement indicates an implementation or derivation",
        "error (Section 5.2); its investigation is in",
        "`docs/freeze/dev_mismatch_investigation_v4.md`.",
        "",
        "Power is the main-operating-point alarm rate and false alarm is the",
        "matched-null alarm rate, both against the per-stratum matched-null",
        "thresholds computed from the same development null rows. The false-alarm",
        "rate is therefore in-sample and optimistic by construction; holdout uses",
        "these thresholds on new graphs. Each distance is `value - threshold`.",
        "",
        "Main operating points (strength map): "
        + ", ".join(f"{s} `{chosen[s]}`" for s in cells_v4.STRUCTURES)
        + ".",
        "",
    ]
    summary = defaultdict(lambda: [0, 0])
    detail = []
    for probe, structure in cells_v4.cells():
        pred = matrix[(probe, structure)]
        power, fa, n_main, n_null = vis[("0.05", probe, structure)]
        obs = label(power, fa)
        agree = obs == pred["prediction"]
        summary[pred["stratum"]][0] += agree
        summary[pred["stratum"]][1] += 1
        sens = []
        for alpha in ("0.01", "0.10"):
            p2, f2, _, _ = vis[(alpha, probe, structure)]
            sens.append(label(p2, f2, blind=BLIND_FOR_ALPHA[alpha]))
        for pv in (0.50, 0.90):
            sens.append(label(power, fa, power_visible=pv))
        for fv in (0.05, 0.15):
            sens.append(label(power, fa, false_alarm_visible=fv))
        detail.append(
            (probe, structure, pred, power, fa, obs, agree, sens, n_main, n_null)
        )
    m += [
        "## Agreement by stratum (main thresholds)",
        "",
        "| Stratum | Agreeing cells | Cells |",
        "|---|---:|---:|",
    ]
    for stratum in ("invariant", "sensitive"):
        m.append(f"| {stratum} | {summary[stratum][0]} | {summary[stratum][1]} |")
    disagreements = [d for d in detail if not d[6]]
    m += [
        "",
        f"Disagreeing cells: {len(disagreements)} "
        f"(invariant {sum(1 for d in disagreements if d[2]['stratum'] == 'invariant')}, "
        f"sensitive {sum(1 for d in disagreements if d[2]['stratum'] == 'sensitive')}).",
        "",
        "## All 42 cells",
        "",
        "Sensitivity columns change one value at a time (Section 8): alpha 0.01 with",
        "blind boundary 0.06; alpha 0.10 with blind boundary 0.15; power for",
        "visible 0.50 and 0.90; false alarm for visible 0.05 and 0.15.",
        "",
        "| Probe | Structure | Stratum | Predicted | Power | Power-0.80 | Power-0.10 | False alarm | FA-0.10 | Observed | Agree | a0.01 | a0.10 | pv0.50 | pv0.90 | fa0.05 | fa0.15 |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|---|---|---|---|",
    ]
    for probe, structure, pred, power, fa, obs, agree, sens, _, _ in detail:
        m.append(
            f"| {probe} | {structure} | {pred['stratum']} | {pred['prediction']} | "
            f"{power:.4f} | {power - 0.80:+.4f} | {power - 0.10:+.4f} | {fa:.4f} | "
            f"{fa - 0.10:+.4f} | {obs} | {'yes' if agree else 'NO'} | "
            + " | ".join(sens)
            + " |"
        )
    m += [
        "",
        f"Rows per cell: {detail[0][8]} main and {detail[0][9]} matched-null "
        "(50 graphs x 32 repeats).",
        "",
        "The smallest-strength sensitivity operating point was not run in",
        "development; its labels are evaluated on the holdout only.",
        "",
    ]
    with mismatch_md.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(m))
    return detail


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--thresholds-md", type=Path, default=THRESHOLDS_MD)
    parser.add_argument("--mismatch-md", type=Path, default=MISMATCH_MD)
    args = parser.parse_args(argv)
    shards = sorted((args.out / "nulls").glob("*.jsonl.gz")) + sorted(
        (args.out / "main").glob("*.jsonl.gz")
    )
    if len(shards) != 8:
        raise SystemExit(f"expected 8 nulls+main shards, found {len(shards)}")
    data = load(shards)
    chosen = read_chosen(args.out / "strength_map_v4.csv")
    rows = calibrate(data)
    vis = visibility(data, rows, chosen)
    detail = write_outputs(
        rows,
        vis,
        chosen,
        shards,
        args.out / "thresholds_v4.csv",
        args.thresholds_md,
        args.mismatch_md,
    )
    n_dis = sum(1 for d in detail if not d[6])
    print(json.dumps({"threshold_rows": len(rows), "disagreements": n_dis}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
