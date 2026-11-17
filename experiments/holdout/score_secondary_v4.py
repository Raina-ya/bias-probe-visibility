"""Task 3-2: secondary endpoints of protocol v4 on the holdout (Sections 11.2-11.5).

Computed once from the same raw rows as the primary endpoint; written before it
is run and committed first.  Every definition below is the registered one:

11.2 decision endpoints (main operating point)
  * coverage C_s(R) = P(certify) for R0 (P0), R1 (designated probe) and the
    structure-agnostic R1 (P2), and the coverage loss C_s(R0) - C_s(R1), per
    structure and pooled, with 95% stratified graph-cluster bootstrap intervals;
  * interception: among units where R0 false-certifies, the fraction R1 does not
    certify, with its count; "insufficient" below 5 units;
  * flip subset (v3 Section 11.4): graphs whose noisy population gap has the
    opposite sign to the ideal gap (or is zero while the ideal is not).  For the
    designated probe, the alarm rate on flipped graphs and on the complement,
    using the decision alarm (clean-E0 threshold), with graph-cluster 95%
    intervals; fewer than 5 graphs is "insufficient".
11.3 visibility agreement for the 42 cells: power = main-point alarm rate
  against the matched-null threshold; false alarm = holdout matched-null alarm
  rate against the same threshold; label by the Section 8 rule; agreement per
  stratum (invariant 23, sensitive 19) with a stratified graph-cluster
  interval; never pooled.  Reported alongside: the Section 8 sensitivity values
  (alpha 0.01 / 0.10 with blind boundaries 0.06 / 0.15; power-for-visible
  0.50 / 0.90; false-alarm-for-visible 0.05 / 0.15) and the smallest-strength
  operating point.
11.4 readout certificate (v3 Section 11.2) for P4a/E4, P4b/E4 and P4b/E5:
  simultaneous Bonferroni Clopper-Pearson intervals (alpha_P = 0.025) for the
  probe events, channels of the structure's frozen grid plus the error-free
  channel retained when every predicted event probability lies inside, and
  B = max over retained channels of b_G(e); certify iff L_T > B, with L_T the
  row's Hoeffding bound (alpha_T = 0.025).  Compared with R0 at the same
  budget.  For E4 the comparison is coverage, not error prevented.
11.5 f*: not evaluable under v4 (docs/part3/holdout_plan_v4.md Section 2).

Bootstrap seeds: SeedSequence([ROOT_SEED, 20, 7, k, 0, ...]) with k = 1
coverage, 2 flip subset, 3 visibility agreement, 4 certificate (k = 0 is the
primary endpoint).  Outputs are written once.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import beta

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "holdout"))
sys.path.insert(0, str(REPO / "experiments" / "development"))

import analysis  # noqa: E402
import analysis_v4  # noqa: E402
import cells_v4  # noqa: E402
import channels  # noqa: E402
import score_primary_v4 as primary  # noqa: E402
import simulate  # noqa: E402
import strength_map  # noqa: E402
from hashing import canonical_sha256  # noqa: E402
from protocol_contract import ROOT_SEED  # noqa: E402

OUT = REPO / "results" / "holdout_v4"
REPORT = REPO / "docs" / "results" / "secondary_endpoints_v4.md"
THRESHOLDS = primary.THRESHOLDS
ALPHA_T = 0.025
ALPHA_P = 0.025
MINIMUM = 5
SENS = {
    "alpha_0.01": dict(alpha="0.01", blind=0.06),
    "alpha_0.10": dict(alpha="0.10", blind=0.15),
    "power_visible_0.50": dict(power_visible=0.50),
    "power_visible_0.90": dict(power_visible=0.90),
    "false_alarm_visible_0.05": dict(false_alarm_visible=0.05),
    "false_alarm_visible_0.15": dict(false_alarm_visible=0.15),
}


def rng(k: int) -> np.random.Generator:
    return np.random.default_rng(
        np.random.SeedSequence([ROOT_SEED, 20, 7, k, 0, 0, 0, 0, 0, 0, 0])
    )


# ---------------------------------------------------------------- inputs


def load_taus(path: Path) -> dict:
    out = {}
    with path.open(encoding="utf-8", newline="") as h:
        for r in csv.DictReader(h):
            out[
                (
                    r["null"],
                    r["alpha"],
                    r["probe"],
                    r["structure"],
                    int(r["width"]),
                    int(r["depth"]),
                )
            ] = float(r["tau"])
    return out


def load_reference(path: Path) -> dict:
    out = {}
    with path.open(encoding="utf-8", newline="") as h:
        for r in csv.DictReader(h):
            out[(r["graph_id"], r["structure"], r["point"])] = r
    return out


def hoeffding_lower(gap: float, n_a: int, n_b: int) -> float:
    return (
        abs(gap)
        - math.sqrt(math.log(4 / ALPHA_T) / (2 * n_a))
        - math.sqrt(math.log(4 / ALPHA_T) / (2 * n_b))
    )


CERT_CELLS = sorted(analysis.CERTIFICATE_CELLS)


def probe_events(probe: str, row: dict, width: int):
    """Observed (count, shots) for the v3 Section 11.2 event list, in a fixed order."""

    probes_ = {c["label"]: c for c in row["circuits"] if c["role"] == "probe"}
    events = []
    if probe == "P4a":
        for label in ("prep0", "prep1"):
            c = probes_[label]
            for q in range(width):
                events.append(
                    (sum(v for z, v in c["counts"].items() if z[q] == "1"), c["shots"])
                )
    else:
        for i, j in itertools.combinations(range(width), 2):
            for prep in ("00", "01", "10", "11"):
                c = probes_[f"pair{i}{j}_prep{prep}"]
                for outcome in ("01", "10", "11"):
                    events.append(
                        (
                            sum(
                                v
                                for z, v in c["counts"].items()
                                if z[i] + z[j] == outcome
                            ),
                            c["shots"],
                        )
                    )
    return events


def predicted_events(probe: str, width: int, readout) -> list[float]:
    def prepared(bits: str) -> np.ndarray:
        v = np.zeros(2**width)
        v[int(bits, 2)] = 1.0
        return channels.apply_readout(v, width, readout)

    strings = simulate.bitstrings(width)
    out = []
    if probe == "P4a":
        for prep in ("0" * width, "1" * width):
            p = prepared(prep)
            for q in range(width):
                out.append(
                    float(sum(p[k] for k, z in enumerate(strings) if z[q] == "1"))
                )
    else:
        for i, j in itertools.combinations(range(width), 2):
            for prep in ("00", "01", "10", "11"):
                bits = ["0"] * width
                bits[i], bits[j] = prep[0], prep[1]
                p = prepared("".join(bits))
                for outcome in ("01", "10", "11"):
                    out.append(
                        float(
                            sum(
                                p[k]
                                for k, z in enumerate(strings)
                                if z[i] + z[j] == outcome
                            )
                        )
                    )
    return out


def channel_grid(structure: str, record) -> dict[str, object]:
    grid = {
        "error_free": channels.Readout(tuple((0.0, 0.0) for _ in range(record.width)))
    }
    for setting, _ in strength_map.GRIDS[structure]:
        condition = channels.parse_condition(structure, setting)
        grid[setting] = channels.readout_for(
            condition, record.width, record.first_edge, record.first_connected_triple
        )
    return grid


def intervals(events) -> tuple[np.ndarray, np.ndarray]:
    k = np.array([e[0] for e in events], dtype=float)
    n = np.array([e[1] for e in events], dtype=float)
    a = ALPHA_P / len(events)
    lo = np.where(k == 0, 0.0, beta.ppf(a / 2, k, n - k + 1))
    hi = np.where(k == n, 1.0, beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


# ---------------------------------------------------------------- loading rows


def load(out: Path, taus, records_by_id, expected_split="holdout"):
    """Per (phase, probe, structure): {graph: arrays}; certificate rows separately."""

    data = defaultdict(lambda: defaultdict(list))
    cert = defaultdict(lambda: defaultdict(list))
    failed = []
    cert_cache = {}
    for phase in ("main", "nulls", "sensitivity"):
        for path in sorted((out / phase).glob("*.jsonl.gz")):
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                for line in handle:
                    entry = json.loads(line)
                    _, probe, structure, _, _, g = entry["unit"]
                    if entry["status"] != "ok":
                        failed.append(entry["unit"])
                        continue
                    w, d = primary.width_depth(g)
                    rows = sorted(entry["rows"], key=lambda r: r["repeat"])
                    for row in rows:
                        if row["split"] != expected_split:
                            raise SystemExit(f"row from split {row['split']}")
                        merged = {"statistic": row["statistic"], **row["components"]}
                        value = None
                        if probe != "P0":
                            value = float(merged[cells_v4.component(probe, structure)])
                        data[(phase, probe, structure)][g].append(
                            (
                                not row["alarm_p0"],
                                row["components"]["gap_target"],
                                value,
                            )
                        )
                        if (
                            phase == "main"
                            and (probe, structure) in analysis.CERTIFICATE_CELLS
                        ):
                            cert[(probe, structure)][g].append(
                                certificate_row(
                                    probe, structure, row, records_by_id[g], cert_cache
                                )
                            )
    return data, cert, failed


def certificate_row(probe, structure, row, record, cache):
    width = record.width
    key = (probe, structure, record.graph_id)
    if key not in cache:
        score = simulate.cut_scores(width, record.edges)
        grid = channel_grid(structure, record)
        cache[key] = (
            {name: predicted_events(probe, width, ro) for name, ro in grid.items()},
            {name: channels.assignment_matrix(width, ro) for name, ro in grid.items()},
            score,
        )
    predicted, matrices, score = cache[key]
    lo, hi = intervals(probe_events(probe, row, width))
    retained = [
        name
        for name, p in predicted.items()
        if np.all((lo <= np.array(p)) & (np.array(p) <= hi))
    ]
    bound = analysis.certificate_bound((probe, structure), score, retained, matrices)
    targets = {c["label"]: 0 for c in row["circuits"] if c["role"] == "target"}
    for c in row["circuits"]:
        if c["role"] == "target":
            targets[c["label"]] += c["shots"]
    lower = hoeffding_lower(
        row["components"]["gap_target"], targets["target0"], targets["target1"]
    )
    return (
        analysis.certify(lower, bound),
        row["components"]["gap_target"],
        bound,
        len(retained),
    )


# ---------------------------------------------------------------- helpers


def stack(per_graph: dict, graphs, index: int) -> np.ndarray:
    return np.array([[r[index] for r in per_graph[g]] for g in graphs])


def winners(gaps: np.ndarray) -> np.ndarray:
    return np.sign(gaps).astype(int)


def boot_interval(stat, strata, generator, n=analysis_v4.BOOTSTRAP):
    values = [stat(analysis.stratified_indices(strata, generator)) for _ in range(n)]
    lo, hi = np.percentile(values, [2.5, 97.5], method="inverted_cdf")
    return float(lo), float(hi)


def cluster_interval(per_graph_rates: np.ndarray, generator, n=analysis_v4.BOOTSTRAP):
    m = per_graph_rates.size
    values = per_graph_rates[generator.integers(0, m, size=(n, m))].mean(axis=1)
    lo, hi = np.percentile(values, [2.5, 97.5], method="inverted_cdf")
    return float(lo), float(hi)


def label(power, fa, power_visible=0.80, false_alarm_visible=0.10, blind=0.10):
    return analysis.classify(
        power, fa, analysis.Thresholds(power_visible, false_alarm_visible, blind)
    )


# ---------------------------------------------------------------- main analysis


def analyse(data, cert, reference, taus, graphs, strata, ideal):
    res = {}
    # --- coverage and interception (11.2)
    gen = rng(1)
    idx_draws = [
        analysis.stratified_indices(strata, gen) for _ in range(analysis_v4.BOOTSTRAP)
    ]
    cov = {}
    for s in cells_v4.STRUCTURES:
        r0 = data[("main", "P0", s)]
        c0 = stack(r0, graphs, 0)
        fc0 = analysis_v4.false_certification(c0, winners(stack(r0, graphs, 1)), ideal)
        entry = {"C_R0": float(c0.mean())}
        for name, probe in (("R1", cells_v4.DESIGNATED[s]), ("R1_P2", "P2")):
            rows = data[("main", probe, s)]
            alarm = np.array(
                [
                    [
                        v
                        > taus[("clean_e0", "0.05", probe, s, *primary.width_depth(g))]
                        for _, _, v in rows[g]
                    ]
                    for g in graphs
                ]
            )
            c1 = stack(rows, graphs, 0) & ~alarm
            loss = (c0.astype(float) - c1).mean(axis=1)
            lo, hi = np.percentile(
                [loss[i].mean() for i in idx_draws], [2.5, 97.5], method="inverted_cdf"
            )
            inter, units = analysis_v4.interception(fc0, c1)
            entry[f"C_{name}"] = float(c1.mean())
            entry[f"loss_{name}"] = float(loss.mean())
            entry[f"loss_{name}_ci"] = [float(lo), float(hi)]
            entry[f"interception_{name}"] = None if math.isnan(inter) else inter
            entry[f"interception_{name}_units"] = units
            cov.setdefault("_loss_" + name, []).append(loss)
            cov.setdefault("_fc0", {})[s] = fc0
            cov.setdefault("_c1_" + name, {})[s] = c1
        res.setdefault("coverage", {})[s] = entry
    for name in ("R1", "R1_P2"):
        pooled = np.mean(cov["_loss_" + name], axis=0)
        lo, hi = np.percentile(
            [pooled[i].mean() for i in idx_draws], [2.5, 97.5], method="inverted_cdf"
        )
        fc0_all = np.concatenate([cov["_fc0"][s] for s in cells_v4.STRUCTURES])
        c1_all = np.concatenate([cov["_c1_" + name][s] for s in cells_v4.STRUCTURES])
        inter, units = analysis_v4.interception(fc0_all, c1_all)
        res.setdefault("coverage_pooled", {})[name] = {
            "loss": float(pooled.mean()),
            "loss_ci": [float(lo), float(hi)],
            "interception": None if math.isnan(inter) else inter,
            "interception_units": units,
        }

    # --- flip subset (11.2, v3 11.4)
    gen = rng(2)
    flips = {}
    for s in cells_v4.STRUCTURES:
        probe = cells_v4.DESIGNATED[s]
        rows = data[("main", probe, s)]
        flipped = [g for g in graphs if reference[(g, s, "main")]["flipped"] == "1"]
        other = [g for g in graphs if g not in flipped]
        out = {"probe": probe, "flipped_graphs": len(flipped)}
        for name, subset in (("flipped", flipped), ("not_flipped", other)):
            if len(subset) < MINIMUM:
                out[name] = "insufficient"
                continue
            rates = np.array(
                [
                    np.mean(
                        [
                            v
                            > taus[
                                ("clean_e0", "0.05", probe, s, *primary.width_depth(g))
                            ]
                            for _, _, v in rows[g]
                        ]
                    )
                    for g in subset
                ]
            )
            out[name] = {
                "alarm_rate": float(rates.mean()),
                "ci": list(cluster_interval(rates, gen)),
                "graphs": len(subset),
            }
        flips[s] = out
    res["flip_subset"] = flips

    # --- visibility agreement (11.3)
    matrix = cells_v4.load_matrix()
    alarms, nulls_, cells_out, sens_point = {}, {}, {}, {}

    def cell_alarm(phase, probe, s, alpha, setting_graphs=graphs):
        rows = data[(phase, probe, s)]
        return np.array(
            [
                [
                    float(
                        v > taus[("matched", alpha, probe, s, *primary.width_depth(g))]
                    )
                    for _, _, v in rows[g]
                ]
                for g in setting_graphs
            ]
        )

    for probe, s in cells_v4.cells():
        a = cell_alarm("main", probe, s, "0.05")
        n = cell_alarm("nulls", probe, s, "0.05")
        alarms[(probe, s)], nulls_[(probe, s)] = a, n
        power, fa = float(a.mean()), float(n.mean())
        sens = {}
        for key, spec in SENS.items():
            if "alpha" in spec:
                p2 = float(cell_alarm("main", probe, s, spec["alpha"]).mean())
                f2 = float(cell_alarm("nulls", probe, s, spec["alpha"]).mean())
                sens[key] = label(p2, f2, blind=spec["blind"])
            else:
                sens[key] = label(power, fa, **spec)
        sp = float(cell_alarm("sensitivity", probe, s, "0.05").mean())
        sens_point[(probe, s)] = label(sp, fa)
        pred = matrix[(probe, s)]
        cells_out[f"{probe}/{s}"] = {
            "stratum": pred["stratum"],
            "predicted": pred["prediction"],
            "power": power,
            "false_alarm": fa,
            "power_minus_0.80": power - 0.80,
            "power_minus_0.10": power - 0.10,
            "false_alarm_minus_0.10": fa - 0.10,
            "observed": label(power, fa),
            "agree": label(power, fa) == pred["prediction"],
            "sensitivity_labels": sens,
            "smallest_strength_power": sp,
            "smallest_strength_label": sens_point[(probe, s)],
        }
    predicted = {c: matrix[c]["prediction"] for c in cells_v4.cells()}
    strata_of = {c: matrix[c]["stratum"] for c in cells_v4.cells()}
    agreement = analysis_v4.stratified_agreement(
        predicted, strata_of, alarms, nulls_, strata, rng(3)
    )
    res["visibility"] = {
        "agreement": {
            k: {"point": v[0], "ci": [v[1], v[2]], "cells": v[3]}
            for k, v in agreement.items()
        },
        "agreement_smallest_strength": {
            st: sum(
                sens_point[c] == predicted[c] for c in predicted if strata_of[c] == st
            )
            for st in ("invariant", "sensitive")
        },
        "cells": cells_out,
    }

    # --- readout certificate (11.4)
    gen = rng(4)
    idx_draws = [
        analysis.stratified_indices(strata, gen) for _ in range(analysis_v4.BOOTSTRAP)
    ]
    certs = {}
    for probe, s in CERT_CELLS:
        rows = cert[(probe, s)]
        cc = np.array([[r[0] for r in rows[g]] for g in graphs])
        fcc = analysis_v4.false_certification(
            cc, winners(np.array([[r[1] for r in rows[g]] for g in graphs])), ideal
        )
        r0 = data[("main", "P0", s)]
        c0 = stack(r0, graphs, 0)
        fc0 = analysis_v4.false_certification(c0, winners(stack(r0, graphs, 1)), ideal)
        bounds = np.array([[r[2] for r in rows[g]] for g in graphs])
        out = {}
        for name, c, f in (("certificate", cc, fcc), ("R0", c0, fc0)):
            cg, fg = c.mean(axis=1), f.mean(axis=1)
            out[name] = {
                "false_certification": float(f.mean()),
                "false_certification_ci": [
                    float(x)
                    for x in np.percentile(
                        [fg[i].mean() for i in idx_draws],
                        [2.5, 97.5],
                        method="inverted_cdf",
                    )
                ],
                "unresolved": float(1 - c.mean()),
                "unresolved_ci": [
                    float(1 - x)
                    for x in np.percentile(
                        [cg[i].mean() for i in idx_draws],
                        [97.5, 2.5],
                        method="inverted_cdf",
                    )
                ],
            }
        finite = bounds[np.isfinite(bounds)]
        out["bound_finite_fraction"] = float(np.isfinite(bounds).mean())
        out["bound_median_finite"] = float(np.median(finite)) if finite.size else None
        out["mean_retained_channels"] = float(
            np.mean([[r[3] for r in rows[g]] for g in graphs])
        )
        certs[f"{probe}/{s}"] = out
    res["readout_certificate"] = certs
    res["f_star"] = (
        "not evaluable under v4: no frozen thresholds at f = 0.05 or 0.25 (holdout plan Section 2); f* = 0 for P0 and P5 by zero probe cost"
    )
    return res


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--skip-input-check", action="store_true", help="tests only")
    parser.add_argument("--records-split", default="holdout", help="tests only")
    parser.add_argument("--expected-split", default="holdout", help="tests only")
    args = parser.parse_args(argv)
    if not args.skip_input_check:
        primary.check_inputs(REPO)
        import run_holdout_v4 as hold

        records = hold.records_after_run(REPO)
    else:
        import run_holdout_v4 as hold

        records = hold.records_from_base(args.records_split)
    by_id = {r.graph_id: r for r in records}
    taus = load_taus(REPO / THRESHOLDS)
    reference = load_reference(args.out / "reference" / "holdout_reference_v4.csv")
    ideal_map = primary.ideal_winners(
        args.out / "reference" / "holdout_reference_v4.csv"
    )
    graphs = sorted(ideal_map, key=primary.graph_order)
    strata = [primary.width_depth(g) for g in graphs]
    ideal = np.array([ideal_map[g] for g in graphs])
    data, cert, failed = load(args.out, taus, by_id, args.expected_split)
    if failed:
        print(json.dumps({"failed_units": failed}))
        return 2
    result = analyse(data, cert, reference, taus, graphs, strata, ideal)
    result["inputs"] = {
        "thresholds_sha256": canonical_sha256(REPO / THRESHOLDS),
        "reference_sha256": canonical_sha256(
            args.out / "reference" / "holdout_reference_v4.csv"
        ),
        "shards": {
            f"{p.parent.name}/{p.name}": canonical_sha256(p)
            for phase in ("main", "nulls", "sensitivity")
            for p in sorted((args.out / phase).glob("*.jsonl.gz"))
        },
    }
    json_path = args.out / "secondary_endpoints_v4.json"
    with json_path.open("x", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x", encoding="utf-8", newline="\n") as h:
        h.write(render(result))
    v = result["visibility"]["agreement"]
    print(
        json.dumps(
            {k: round(x["point"], 4) for k, x in v.items()}
            | {"json_sha256": canonical_sha256(json_path)}
        )
    )
    return 0


def fmt(x, digits=4):
    return "n/a" if x is None else f"{x:.{digits}f}"


def render(r: dict) -> str:
    L = [
        "# Secondary endpoints, protocol v4 holdout (Task 3-2)",
        "",
        "Evidence type: noisy simulation, holdout split 20 (the single run of Task",
        "3-1). Secondary endpoints of protocol v4 Sections 11.2--11.5; none of them",
        "changes the primary outcome. Recomputable with",
        "`experiments/holdout/score_secondary_v4.py`, which was committed before it",
        "was first run.",
        "",
        "## 1. Coverage and interception (main operating point)",
        "",
        "| Structure | C(R0) | C(R1) | Loss R1 [95% CI] | Interception R1 (units) | C(R1, P2) | Loss P2 [95% CI] | Interception P2 (units) |",
        "|---|---:|---:|---|---|---:|---|---|",
    ]
    for s, e in r["coverage"].items():

        def inter(name, e=e):
            v = e[f"interception_{name}"]
            return (
                "insufficient" if v is None else f"{v:.3f}"
            ) + f" ({e[f'interception_{name}_units']})"

        L.append(
            f"| {s} | {e['C_R0']:.4f} | {e['C_R1']:.4f} | {e['loss_R1']:+.4f} [{e['loss_R1_ci'][0]:+.4f}, {e['loss_R1_ci'][1]:+.4f}] | {inter('R1')} | "
            f"{e['C_R1_P2']:.4f} | {e['loss_R1_P2']:+.4f} [{e['loss_R1_P2_ci'][0]:+.4f}, {e['loss_R1_P2_ci'][1]:+.4f}] | {inter('R1_P2')} |"
        )
    for name, e in r["coverage_pooled"].items():
        share = (
            "insufficient" if e["interception"] is None else f"{e['interception']:.3f}"
        )
        L.append(
            f"| pooled {name} | | | {e['loss']:+.4f} [{e['loss_ci'][0]:+.4f}, {e['loss_ci'][1]:+.4f}] | "
            f"{share} ({e['interception_units']}) | | | |"
        )
    L += [
        "",
        "## 2. Flip subset (descriptive; designated probe, decision alarm)",
        "",
        "| Structure | Probe | Flipped graphs | Alarm rate, flipped [95% CI] | Alarm rate, not flipped [95% CI] |",
        "|---|---|---:|---|---|",
    ]
    for s, e in r["flip_subset"].items():

        def part(x):
            return (
                x
                if isinstance(x, str)
                else f"{x['alarm_rate']:.4f} [{x['ci'][0]:.4f}, {x['ci'][1]:.4f}] (n={x['graphs']})"
            )

        L.append(
            f"| {s} | {e['probe']} | {e['flipped_graphs']} | {part(e['flipped'])} | {part(e['not_flipped'])} |"
        )
    v = r["visibility"]
    L += [
        "",
        "## 3. Visibility agreement (42 cells, never pooled)",
        "",
        "| Stratum | Agreement [95% CI] | Cells | Agreement at smallest strength |",
        "|---|---|---:|---:|",
    ]
    for st, e in v["agreement"].items():
        L.append(
            f"| {st} | {e['point']:.4f} [{e['ci'][0]:.4f}, {e['ci'][1]:.4f}] | {e['cells']} | {v['agreement_smallest_strength'][st]} / {e['cells']} |"
        )
    keys = list(SENS)
    L += [
        "",
        "| Cell | Stratum | Predicted | Power | Power-0.80 | Power-0.10 | False alarm | FA-0.10 | Observed | Agree | "
        + " | ".join(keys)
        + " | Smallest-strength label |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|" + "---|" * len(keys) + "---|",
    ]
    for cell, e in v["cells"].items():
        L.append(
            f"| {cell} | {e['stratum']} | {e['predicted']} | {e['power']:.4f} | {e['power_minus_0.80']:+.4f} | {e['power_minus_0.10']:+.4f} | "
            f"{e['false_alarm']:.4f} | {e['false_alarm_minus_0.10']:+.4f} | {e['observed']} | {'yes' if e['agree'] else 'NO'} | "
            + " | ".join(e["sensitivity_labels"][k] for k in keys)
            + f" | {e['smallest_strength_label']} |"
        )
    L += [
        "",
        "## 4. Readout certificate (v3 Section 11.2), compared with R0",
        "",
        "| Cell | Rule | False certification [95% CI] | Unresolved [95% CI] |",
        "|---|---|---|---|",
    ]
    for cell, e in r["readout_certificate"].items():
        for name in ("certificate", "R0"):
            x = e[name]
            L.append(
                f"| {cell} | {name} | {x['false_certification']:.4f} [{x['false_certification_ci'][0]:.4f}, {x['false_certification_ci'][1]:.4f}] | "
                f"{x['unresolved']:.4f} [{x['unresolved_ci'][0]:.4f}, {x['unresolved_ci'][1]:.4f}] |"
            )
        L.append(
            f"| {cell} | bound | finite fraction {e['bound_finite_fraction']:.3f}; median finite B {fmt(e['bound_median_finite'])}; "
            f"mean retained channels {e['mean_retained_channels']:.2f} | |"
        )
    L += [
        "",
        "E4 never flips a decision (Section 4.1), so for E4 the comparison is",
        "coverage gained or lost, not error prevented.",
        "",
        "## 5. Probe fraction f*",
        "",
        r["f_star"] + ".",
        "",
    ]
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
