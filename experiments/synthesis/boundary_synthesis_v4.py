"""Task 4-1: visibility boundary map and failure-cause classification (protocol v4).

Reads only committed results:
  results/holdout_v4/secondary_endpoints_v4.json   holdout labels and powers
  results/holdout_v4/primary_endpoint_v4.json      decision endpoint
  results/holdout_v4/reference/holdout_reference_v4.csv  beta/Delta per graph
  results/prop1/prop1_scoring_v4.json              Proposition-1 test
  docs/freeze/dev_mismatch_v4.md                   development labels
  docs/theory/06_matrix_v4.csv                     predictions and strata
Optionally (exploratory, if the gitignored holdout shards exist) the P1b
statistic, calibrated in-sample on the holdout matched-null rows.

Writes, once: figures/boundary_map_v4.svg (pure-Python SVG, byte-stable
across platforms), docs/results/boundary_synthesis_v4.md, and
results/synthesis/boundary_synthesis_v4.json.

The cause classification is an interpretation (exploratory). Its rules are fixed
in CAUSE_RULES below and applied mechanically to every disagreement; the
evidence for each rule is stated with the cell.
"""

from __future__ import annotations

import csv
import gzip
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import cells_v4  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

SECONDARY = Path("results/holdout_v4/secondary_endpoints_v4.json")
PRIMARY = Path("results/holdout_v4/primary_endpoint_v4.json")
REFERENCE = Path("results/holdout_v4/reference/holdout_reference_v4.csv")
PROP1 = Path("results/prop1/prop1_scoring_v4.json")
DEV_MISMATCH = Path("docs/freeze/dev_mismatch_v4.md")
FIGURE = Path("figures/boundary_map_v4.svg")
REPORT = Path("docs/results/boundary_synthesis_v4.md")
JSON_OUT = Path("results/synthesis/boundary_synthesis_v4.json")
PROBES = ("P1", "P2", "P3", "P4a", "P4b", "P5")

CAUSE_RULES = {
    "design": "a protocol choice made before data (calibration sample, degenerate threshold, endpoint definition) produces the outcome",
    "method": "the probe statistic or decision rule behaves differently from its derivation at finite shots",
    "resources": "the population contrast exists but the fixed budget gives power below the label threshold",
    "model": "the derivation's effect-size assessment was wrong in the conservative direction (more power than predicted)",
}


def classify_cell(cell: dict) -> tuple[str, str]:
    pred, obs, power, fa = (
        cell["predicted"],
        cell["observed"],
        cell["power"],
        cell["false_alarm"],
    )
    if cell["stratum"] == "invariant":
        if abs(power - fa) <= 0.02:
            return "design", (
                f"power {power:.3f} equals the matched-null alarm rate {fa:.3f}: the statistic does not respond; "
                "the label comes from a null alarm rate above alpha against development thresholds calibrated on two graphs per stratum"
            )
        return "method", (
            f"power {power:.3f} versus null {fa:.3f}: the population statistic is invariant but its finite-shot "
            "distribution is not (pre-lock investigation for P5/E1)"
        )
    if pred == "visible" and obs == "partial":
        return (
            "resources",
            f"power {power:.3f} is above 0.10 but below 0.80 at n_P = 1,638",
        )
    if pred == "partial" and obs == "blind":
        return (
            "resources",
            f"power {power:.3f} does not exceed 0.10: the contrast is below what the budget can detect",
        )
    if pred == "partial" and obs == "visible":
        return (
            "model",
            f"power {power:.3f} reaches 0.80 with false alarm {fa:.3f}: the derivation underestimated the effect",
        )
    return "design", f"predicted {pred}, observed {obs}"


def dev_labels(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if (
            len(parts) > 10
            and parts[0] in PROBES
            and parts[3] in ("visible", "partial", "blind")
        ):
            out[f"{parts[0]}/{parts[1]}"] = parts[9]
    return out


def beta_over_delta(path: Path) -> dict:
    vals = defaultdict(list)
    flips = defaultdict(int)
    with path.open(encoding="utf-8", newline="") as h:
        for r in csv.DictReader(h):
            g, n = float(r["ideal_gap"]), float(r["noisy_population_gap"])
            if abs(g) <= 1e-12:
                continue
            key = (r["structure"], r["point"])
            vals[key].append((n - g) * (1 if g > 0 else -1) / abs(g))
            flips[key] += r["flipped"] == "1"
    return {
        f"{s}|{p}": {"median": statistics.median(v), "flipped_graphs": flips[(s, p)]}
        for (s, p), v in sorted(vals.items())
    }


def p1b_exploratory(repo: Path) -> dict | None:
    out_dir = repo / "results" / "holdout_v4"
    if not any((out_dir / "main").glob("*.gz")):
        return None
    vals = defaultdict(lambda: defaultdict(list))
    for phase in ("main", "nulls"):
        for path in sorted((out_dir / phase).glob("*.jsonl.gz")):
            with gzip.open(path, "rt", encoding="utf-8") as h:
                for line in h:
                    e = json.loads(line)
                    _, probe, s, _, _, g = e["unit"]
                    if probe != "P1" or e["status"] != "ok":
                        continue
                    stratum = tuple(int(x[1:]) for x in g.split("-")[1:3])
                    for row in e["rows"]:
                        vals[(phase, s)][stratum].append(row["components"]["p1b_w_neg"])
    result = {}
    for s in cells_v4.STRUCTURES:
        hits = total = 0
        for stratum, nulls in vals[("nulls", s)].items():
            ranked = sorted(nulls)
            tau = ranked[min(len(ranked), -(-(len(ranked) + 1) * 95 // 100)) - 1]
            main = vals[("main", s)][stratum]
            hits += sum(v > tau for v in main)
            total += len(main)
        result[s] = hits / total if total else None
    return result


# ---------------------------------------------------------------- SVG


def colour(p: float) -> str:
    """Sequential blue scale, light (0) to dark (1)."""

    stops = [
        (0.0, (239, 243, 255)),
        (0.25, (189, 215, 238)),
        (0.5, (107, 174, 214)),
        (0.75, (33, 113, 181)),
        (1.0, (8, 48, 107)),
    ]
    for (a, ca), (b, cb) in zip(stops, stops[1:], strict=False):
        if p <= b:
            t = (p - a) / (b - a) if b > a else 0
            return "#%02x%02x%02x" % tuple(
                round(x + t * (y - x)) for x, y in zip(ca, cb, strict=True)
            )
    return "#08306b"


def svg(cells: dict, bd: dict) -> str:
    cw, ch, left, top = 104, 58, 70, 92
    width, height = left + cw * 7 + 20, top + ch * 6 + 96
    letter = {"visible": "V", "partial": "P", "blind": "B"}
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        '<text x="10" y="22" font-size="15" font-weight="bold" fill="#111">Holdout visibility: alarm rate at the smallest | main strength</text>',
        '<text x="10" y="40" font-size="11" fill="#444">Cell text: predicted &#8594; observed label (V visible, P partial, B blind). Red outline: disagreement. Grey hatch: invariant stratum.</text>',
    ]
    for j, s in enumerate(cells_v4.STRUCTURES):
        x = left + j * cw
        out.append(
            f'<text x="{x + cw / 2}" y="{top - 26}" font-size="13" font-weight="bold" text-anchor="middle" fill="#111">{s.replace(chr(39), "&#8242;")}</text>'
        )
        m = bd.get(f"{s}|main", {}).get("median")
        out.append(
            f'<text x="{x + cw / 2}" y="{top - 10}" font-size="10" text-anchor="middle" fill="#444">&#946;/&#916; {m:+.2f}</text>'
            if m is not None
            else ""
        )
    for i, p in enumerate(PROBES):
        y = top + i * ch
        out.append(
            f'<text x="{left - 10}" y="{y + ch / 2 + 4}" font-size="13" font-weight="bold" text-anchor="end" fill="#111">{p}</text>'
        )
        for j, s in enumerate(cells_v4.STRUCTURES):
            c = cells[f"{p}/{s}"]
            x = left + j * cw
            half = (cw - 6) / 2
            for k, val in enumerate((c["smallest_strength_power"], c["power"])):
                out.append(
                    f'<rect x="{x + 3 + k * half}" y="{y + 3}" width="{half}" height="{ch - 6}" fill="{colour(val)}"/>'
                )
            if c["stratum"] == "invariant":
                out.append(
                    f'<rect x="{x + 3}" y="{y + 3}" width="{cw - 6}" height="{ch - 6}" fill="url(#hatch)"/>'
                )
            stroke = "#d62728" if not c["agree"] else "#ffffff"
            sw = 3 if not c["agree"] else 1
            out.append(
                f'<rect x="{x + 3}" y="{y + 3}" width="{cw - 6}" height="{ch - 6}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>'
            )
            txt = "#111111"
            halo = 'stroke="#ffffff" stroke-width="3" paint-order="stroke" stroke-linejoin="round"'
            out.append(
                f'<text x="{x + cw / 2}" y="{y + ch / 2 - 2}" font-size="12" font-weight="bold" text-anchor="middle" fill="{txt}" {halo}>{letter[c["predicted"]]}&#8594;{letter[c["observed"]]}</text>'
            )
            out.append(
                f'<text x="{x + cw / 2}" y="{y + ch / 2 + 14}" font-size="10" text-anchor="middle" fill="{txt}" {halo}>{c["smallest_strength_power"]:.2f} | {c["power"]:.2f}</text>'
            )
    ly = top + ch * 6 + 28
    for k in range(11):
        out.append(
            f'<rect x="{left + k * 30}" y="{ly}" width="30" height="12" fill="{colour(k / 10)}"/>'
        )
    out.append(f'<text x="{left}" y="{ly + 28}" font-size="10" fill="#444">0</text>')
    out.append(
        f'<text x="{left + 330}" y="{ly + 28}" font-size="10" text-anchor="end" fill="#444">1  alarm rate against the matched-null threshold</text>'
    )
    out.insert(
        2,
        '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#9e9e9e" stroke-width="1" stroke-opacity="0.45"/></pattern></defs>',
    )
    out.append("</svg>")
    return "\n".join(x for x in out if x) + "\n"


# ---------------------------------------------------------------- main


def main(argv=None) -> int:
    sec = json.loads((REPO / SECONDARY).read_text(encoding="utf-8"))
    pri = json.loads((REPO / PRIMARY).read_text(encoding="utf-8"))
    prop1 = json.loads((REPO / PROP1).read_text(encoding="utf-8"))
    cells = sec["visibility"]["cells"]
    dev = dev_labels(REPO / DEV_MISMATCH)
    bd = beta_over_delta(REPO / REFERENCE)
    p1b = p1b_exploratory(REPO)

    rows = []
    for p, s in cells_v4.cells():
        c = cells[f"{p}/{s}"]
        cause, why = ("", "")
        if not c["agree"]:
            cause, why = classify_cell(c)
        rows.append(
            {
                "cell": f"{p}/{s}",
                "stratum": c["stratum"],
                "predicted": c["predicted"],
                "development": dev.get(f"{p}/{s}"),
                "holdout": c["observed"],
                "smallest_strength": c["smallest_strength_label"],
                "power": c["power"],
                "false_alarm": c["false_alarm"],
                "agree": c["agree"],
                "cause": cause,
                "evidence": why,
            }
        )
    decision_failures = [
        {
            "item": "R1 coverage under E4, E5, E5', E6",
            "cause": "design",
            "evidence": "P4a's clean-E0 threshold is 0 (degenerate null); any readout flip alarms, so C(R1) = 0 (secondary endpoint)",
        },
        {
            "item": "R1 coverage under E1",
            "cause": "method",
            "evidence": f"C(R1) {sec['coverage']['E1']['C_R1']:.3f} versus C(R0) {sec['coverage']['E1']['C_R0']:.3f}; P1 alarms on most non-flipped graphs and only 0.065 on flipped ones",
        },
        {
            "item": "Readout certificate unresolved",
            "cause": "resources",
            "evidence": "P4b spreads n_P over 4*C(w,2) circuits; simultaneous intervals retain channels whose bound exceeds L_T (secondary endpoint)",
        },
        {
            "item": "f* not evaluable",
            "cause": "design",
            "evidence": "no development thresholds at f = 0.05 or 0.25",
        },
        {
            "item": "Proposition-1 directional misses (8)",
            "cause": "method",
            "evidence": "all in unresolved_anchor graphs, where the rule defaults to Raw without certification",
        },
        {
            "item": "Proposition-1 ties counted as misses (47)",
            "cause": "design",
            "evidence": "registered hit definition; 42 graphs had zero errors for both methods",
        },
    ]
    stable = sum(r["development"] == r["holdout"] for r in rows if r["development"])
    result = {
        "cells": rows,
        "decision_failures": decision_failures,
        "beta_over_delta": bd,
        "p1b_exploratory_power": p1b,
        "dev_holdout_label_agreement": stable,
        "cause_rules": CAUSE_RULES,
        "inputs": {
            str(x): canonical_sha256(REPO / x)
            for x in (SECONDARY, PRIMARY, REFERENCE, PROP1, DEV_MISMATCH)
        },
    }
    (REPO / JSON_OUT).parent.mkdir(parents=True, exist_ok=True)
    with (REPO / JSON_OUT).open("x", encoding="utf-8", newline="\n") as h:
        h.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    (REPO / FIGURE).parent.mkdir(parents=True, exist_ok=True)
    with (REPO / FIGURE).open("x", encoding="utf-8", newline="\n") as h:
        h.write(svg(cells, bd))
    m = pri["primary_designated"]["main"]
    counts = defaultdict(int)
    for r in rows:
        if r["cause"]:
            counts[r["cause"]] += 1
    L = (
        [
            "# Visibility boundary and failure causes, protocol v4 (Task 4-1)",
            "",
            "Evidence type: noisy simulation (holdout split 20, read once; Proposition-1",
            "splits 30/31). Labels and endpoints are confirmatory or secondary as",
            "registered; the cause classification and the P1b comparison are exploratory",
            "interpretations. Generated by `experiments/synthesis/boundary_synthesis_v4.py`",
            "from committed results only.",
            "",
            "## Figure",
            "",
            "![Boundary map](../../figures/boundary_map_v4.svg)",
            "",
            "**Figure 1. Only readout probes on readout structures and the symmetry probe on",
            "symmetry-breaking structures reach visibility; most cells stay blind as",
            "predicted, and the failures concentrate in the budget-sensitive stratum.**",
            "Each cell shows the holdout alarm rate against the matched-null threshold at",
            "the smallest frozen strength (left half) and the main strength (right half),",
            "the predicted and observed label, and a red outline where they disagree.",
            "Column headers give the median beta/Delta of the main point over the 100",
            "holdout graphs.",
            "",
            "## 1. Summary",
            "",
            f"- Primary endpoint: {m['outcome']}, dFC {m['dFC']:+.4f} "
            f"[{m['dFC_lower_2.5']:+.4f}, {m['dFC_upper_97.5']:+.4f}], coverage loss {m['coverage_loss_pooled']:.3f}.",
            f"- Visibility agreement: invariant {sec['visibility']['agreement']['invariant']['point']:.3f}, "
            f"sensitive {sec['visibility']['agreement']['sensitive']['point']:.3f} (never pooled).",
            f"- Development and holdout labels coincide in {stable} of 42 cells.",
            f"- Proposition-1 hit rate {prop1['summary']['hits']}/100 (ties {prop1['summary']['ties']}).",
            "- Cell disagreements by cause: "
            + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
            + ".",
            "",
            "Cause rules (applied mechanically):",
            "",
        ]
        + [f"- **{k}**: {v}." for k, v in CAUSE_RULES.items()]
        + [
            "",
            "## 2. All 42 cells",
            "",
            "| Cell | Stratum | Predicted | Development | Holdout | Smallest strength | Power | False alarm | Cause | Evidence |",
            "|---|---|---|---|---|---|---:|---:|---|---|",
        ]
    )
    for r in rows:
        L.append(
            f"| {r['cell']} | {r['stratum']} | {r['predicted']} | {r['development']} | "
            f"{r['holdout']}{'' if r['agree'] else ' **(disagrees)**'} | {r['smallest_strength']} | "
            f"{r['power']:.3f} | {r['false_alarm']:.3f} | {r['cause'] or '-'} | {r['evidence'] or '-'} |"
        )
    L += [
        "",
        "## 3. Decision-level failures",
        "",
        "| Item | Cause | Evidence |",
        "|---|---|---|",
    ]
    L += [
        f"| {d['item']} | {d['cause']} | {d['evidence']} |" for d in decision_failures
    ]
    L += [
        "",
        "## 4. beta/Delta by structure (holdout reference, exact probabilities)",
        "",
        "| Structure | Point | Median beta/Delta | Flipped graphs |",
        "|---|---|---:|---:|",
    ]
    for k, v in bd.items():
        s, p = k.split("|")
        L.append(f"| {s} | {p} | {v['median']:+.4f} | {v['flipped_graphs']} |")
    L += ["", "## 5. Exploratory: P1b and GVS", ""]
    if p1b:
        L.append(
            "P1b (negative quasi-probability weight from P1 counts), alarm rate at the main point against an"
        )
        L.append(
            "in-sample 95th-percentile threshold from the holdout matched-null rows per stratum:"
        )
        L.append("")
        L.append(
            "| Structure | P1b power (exploratory, in-sample threshold) | P1 power (registered) |"
        )
        L.append("|---|---:|---:|")
        for s in cells_v4.STRUCTURES:
            L.append(f"| {s} | {p1b[s]:.3f} | {cells[f'P1/{s}']['power']:.3f} |")
    else:
        L.append(
            "P1b not computed: the holdout raw shards are not present on this machine."
        )
    L += [
        "",
        "GVS was not implemented (`src/probes.py` raises `NotImplementedError`: its",
        "L_C and K definitions were never frozen). This follows the registered scope-cut",
        "order, in which GVS is cut first. It is reported as not run.",
        "",
    ]
    with (REPO / REPORT).open("x", encoding="utf-8", newline="\n") as h:
        h.write("\n".join(L))
    print(
        json.dumps(
            {
                "disagreements_by_cause": dict(counts),
                "dev_holdout_same_label": stable,
                "figure_sha256": canonical_sha256(REPO / FIGURE),
                "p1b": p1b is not None,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
