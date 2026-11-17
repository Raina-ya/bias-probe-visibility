"""Task 3-3 step 2: score the registered Proposition-1 predictions (split 31), once.

Refuses unless docs/freeze/registration_prop1_v4.json exists, names an OSF
record, and lists the SHA-256 of results/prop1/predictions.csv that is on disk.
The same K = 4 candidate circuits as the pilot are run under the same E1 noise
with split-31 shot seeds: 32 repeats, 16,384 shots per method per repeat
(Raw: 4 x 4,096; ZNE: 16,384 over 4 candidates x 3 scales).

For each repeat a method selects the candidate with the largest estimate; a
non-unique maximum is an error, and so is any selection when the ideal best
candidate is not unique (gap <= 1e-12).  The ideal is read only here, from
noiseless scale-1 probabilities.  A hit is a strictly lower error rate for the
predicted method; an exact tie is a miss.  The hit rate gets a 95% Wilson
interval (z = 1.96) across the 100 graphs.  Writes the single-run marker
results/run_markers_v4/prop1_scoring.success.
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np

import prop1_v4 as p

REPO = p.REPO
sys.path.insert(0, str(REPO / "src"))

import analysis  # noqa: E402
import execution  # noqa: E402
import simulate  # noqa: E402
import split_guard_v4  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

REPORT = REPO / "docs" / "results" / "prop1_prediction_test_v4.md"


def check_registration(out: Path) -> dict:
    path = REPO / p.REGISTRATION
    if not path.is_file():
        raise SystemExit(
            "refused: predictions not registered (no registration_prop1_v4.json)"
        )
    record = json.loads(path.read_text(encoding="utf-8"))
    for key in ("registry", "url", "timestamp_utc", "commit", "files"):
        if not record.get(key):
            raise SystemExit(f"refused: registration lacks {key}")
    rel = (out / "predictions.csv").relative_to(REPO).as_posix()
    if record["files"].get(rel) != canonical_sha256(out / "predictions.csv"):
        raise SystemExit("refused: predictions.csv differs from the registered hash")
    split_guard_v4.require_split(REPO, p.SCORING_SPLIT)
    return record


def selection_errors(values: np.ndarray, ideal_best: int | None) -> int:
    best = np.flatnonzero(values == values.max())
    return int(ideal_best is None or best.size != 1 or best[0] != ideal_best)


def score_graph(record, cache) -> dict:
    trios = p.candidate_circuits(record, p.PILOT_SPLIT)
    probs = [[cache.get(c, p.NOISE) for c in trio] for trio in trios]
    score = simulate.cut_scores(record.width, record.edges)
    ideal = np.array(
        [float(cache.get(trio[0], simulate.NO_GATE_NOISE) @ score) for trio in trios]
    )
    order = np.sort(ideal)
    ideal_best = int(np.argmax(ideal)) if order[-1] - order[-2] > 1e-12 else None
    errors = {"raw": 0, "zne": 0}
    repeats = []
    for r in range(p.SCORING_REPEATS):
        counts = p.draw_block(
            p.shot_rng(p.SCORING_SPLIT, record, r), probs, record.width, p.SCORING_SHOTS
        )
        raw, zne = p.estimates(counts, score)
        errors["raw"] += selection_errors(raw, ideal_best)
        errors["zne"] += selection_errors(zne, ideal_best)
        repeats.append(counts)
    return {
        "graph_id": record.graph_id,
        "ideal_scores": ideal.tolist(),
        "ideal_best": ideal_best,
        "error_rate_raw": errors["raw"] / p.SCORING_REPEATS,
        "error_rate_zne": errors["zne"] / p.SCORING_REPEATS,
        "repeats": repeats,
    }


def run(args) -> int:
    registration = check_registration(args.out)
    marker = split_guard_v4.marker_path(REPO, p.SCORING_SPLIT)
    with (args.out / "predictions.csv").open(encoding="utf-8", newline="") as h:
        predictions = {r["graph_id"]: r for r in csv.DictReader(h)}
    recs = p.records()
    if set(predictions) != {r.graph_id for r in recs}:
        raise SystemExit("refused: predictions do not cover the 100 graphs")
    started, cache, results = time.perf_counter(), execution.SolveCache(), []
    raw_path = args.out / "scoring" / "scoring_raw_v4.jsonl.gz"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(raw_path, "xt", encoding="utf-8") as h:
        for record in recs:
            entry = score_graph(record, cache)
            h.write(json.dumps(entry, sort_keys=True) + "\n")
            pred = predictions[record.graph_id]["prediction"]
            er, ez = entry["error_rate_raw"], entry["error_rate_zne"]
            hit = (pred == "zne" and ez < er) or (pred == "raw" and er < ez)
            results.append(
                {
                    "graph_id": record.graph_id,
                    "prediction": pred,
                    "diagnostic_reason": predictions[record.graph_id][
                        "diagnostic_reason"
                    ],
                    "error_rate_raw": er,
                    "error_rate_zne": ez,
                    "tie": er == ez,
                    "hit": bool(hit),
                    "ideal_best_unique": entry["ideal_best"] is not None,
                }
            )
    hits = sum(r["hit"] for r in results)
    lo, hi = analysis.wilson_interval(hits, len(results))
    summary = {
        "graphs": len(results),
        "hits": hits,
        "hit_rate": hits / len(results),
        "wilson_95": [lo, hi],
        "ties": sum(r["tie"] for r in results),
        "predicted_zne": sum(r["prediction"] == "zne" for r in results),
        "zne_better_observed": sum(
            r["error_rate_zne"] < r["error_rate_raw"] for r in results
        ),
        "raw_better_observed": sum(
            r["error_rate_raw"] < r["error_rate_zne"] for r in results
        ),
        "registration": {
            k: registration[k] for k in ("url", "timestamp_utc", "commit")
        },
        "commit": args.commit,
        "seconds": time.perf_counter() - started,
        "scoring_raw_sha256": canonical_sha256(raw_path),
    }
    by_reason = {}
    for r in results:
        d = by_reason.setdefault(r["diagnostic_reason"], {"graphs": 0, "hits": 0})
        d["graphs"] += 1
        d["hits"] += r["hit"]
    summary["by_reason"] = by_reason
    out_json = args.out / "prop1_scoring_v4.json"
    with out_json.open("x", encoding="utf-8", newline="\n") as h:
        h.write(
            json.dumps(
                {"summary": summary, "graphs": results}, indent=1, sort_keys=True
            )
            + "\n"
        )
    marker.parent.mkdir(parents=True, exist_ok=True)
    with marker.open("x", encoding="utf-8", newline="\n") as h:
        h.write(
            json.dumps(
                {"commit": args.commit, "result_sha256": canonical_sha256(out_json)},
                indent=1,
            )
            + "\n"
        )
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = (
        [
            "# Proposition-1 prediction test, protocol v4 (Task 3-3)",
            "",
            "Evidence type: noisy simulation (E1 depolarizing, p = 0.04), splits 30",
            "(pilot) and 31 (scoring), run once. Secondary endpoint. Predictions were",
            f"registered at {registration['url']} ({registration['timestamp_utc']}) before scoring.",
            "",
            f"**Hit rate: {hits}/{len(results)} = {hits / len(results):.3f}, 95% Wilson [{lo:.3f}, {hi:.3f}].**",
            "",
            f"- Predicted ZNE: {summary['predicted_zne']} graphs; observed ZNE better: "
            f"{summary['zne_better_observed']}; observed Raw better: {summary['raw_better_observed']}; "
            f"exact ties (misses): {summary['ties']}.",
            "",
            "| Diagnostic reason | Graphs | Hits |",
            "|---|---:|---:|",
        ]
        + [
            f"| {k} | {v['graphs']} | {v['hits']} |"
            for k, v in sorted(by_reason.items())
        ]
        + [
            "",
            "Per-graph results: `results/prop1/prop1_scoring_v4.json`.",
            "",
        ]
    )
    with REPORT.open("x", encoding="utf-8", newline="\n") as h:
        h.write("\n".join(lines))
    print(
        json.dumps(
            {
                k: summary[k]
                for k in ("hits", "hit_rate", "wilson_95", "ties", "predicted_zne")
            }
        )
    )
    return 0
