"""Task 3-1: the single holdout run of protocol v4 (split 20).

Phases, run in this order (docs/part3/holdout_plan_v4.md):

  plan          counts only; builds the manifest, draws no shots
  main          P0-P5 x 7 structures x 100 graphs at the main operating point
  nulls         P1-P5 x 7 matched nulls x 100 graphs
  sensitivity   P1-P5 x 7 structures x 100 graphs at the smallest strength
  finalize      checks that every unit is present exactly once and writes the
                single-run marker results/run_markers_v4/holdout.success
  reference     after the marker only: ideal and noisy population gaps used
                for scoring (Section 11.1: scored after all decisions exist)

Every unit is 32 repeats at f = 0.10 (zero-extra probes use f = 0).  Rules:

* Run phases require the confirmatory lock (split_guard_v4), HEAD == --commit,
  clean tracked files, a clean experiments/holdout, an absent marker, and the
  strength map whose hash the lock records.
* A shard file is written once (exclusive create).  A unit that raises is kept
  with its traceback and is never rerun.  A process that ends before writing its
  shard leaves no rows; rerunning that shard at the same commit is permitted and
  reproduces the same rows, because every draw comes from its frozen seed key.
  The run log keeps the aborted start.
* After the marker exists, split_guard_v4 refuses the holdout for every run
  phase.  Post-run steps rebuild the manifest with ``records_after_run``, which
  requires the marker.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "development"))

import cells_v4  # noqa: E402
import execution  # noqa: E402
import manifest as base  # noqa: E402
import manifest_v4  # noqa: E402
import protocol_contract as contract  # noqa: E402
import reference  # noqa: E402
import run_development_v4 as dev  # noqa: E402
import runner  # noqa: E402
import split_guard_v4  # noqa: E402
import strength_map  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

SPLIT = "holdout"
REPEATS = dev.REPEATS
PROBES = dev.PROBES
BIAS_PROBES = dev.NULL_PROBES
OUT = REPO / "results" / "holdout_v4"
RUN_PHASES = ("main", "nulls", "sensitivity")
STRENGTH_MAP = Path("results/development_v4/strength_map_v4.csv")


# ---------------------------------------------------------------- lock inputs


def locked_chosen(repo: Path = REPO) -> dict[tuple[str, str], str]:
    """Operating points from the strength map, checked against the lock."""

    lock = json.loads(
        (repo / split_guard_v4.CONFIRMATORY_LOCK).read_text(encoding="utf-8")
    )
    product = lock["products"]["strength_map"]
    if product["path"] != STRENGTH_MAP.as_posix():
        raise RuntimeError("strength-map path differs from the lock")
    if canonical_sha256(repo / STRENGTH_MAP) != product["sha256"]:
        raise RuntimeError("strength map differs from the confirmatory lock")
    return dev.read_chosen(repo / STRENGTH_MAP)


# ---------------------------------------------------------------- work units


def main_units(records, chosen):
    return [("main",) + u[1:] for u in dev.main_units(records, chosen)]


def null_units(records):
    units = []
    for probe in BIAS_PROBES:
        for structure in cells_v4.STRUCTURES:
            index = len(strength_map.GRIDS[structure])
            for r in records:
                units.append(
                    (
                        "nulls",
                        probe,
                        structure,
                        cells_v4.MATCHED_NULL[structure],
                        index,
                        r.graph_id,
                    )
                )
    return units


def sensitivity_units(records, chosen):
    units = []
    for probe in BIAS_PROBES:
        for structure in cells_v4.STRUCTURES:
            setting = chosen[(structure, "sensitivity")]
            for r in records:
                units.append(
                    (
                        "sensitivity",
                        probe,
                        structure,
                        setting,
                        dev.setting_index(structure, setting),
                        r.graph_id,
                    )
                )
    return units


def units_for(phase, records, chosen):
    return {
        "main": lambda: main_units(records, chosen),
        "nulls": lambda: null_units(records),
        "sensitivity": lambda: sensitivity_units(records, chosen),
    }[phase]()


def all_units(records, chosen):
    return [u for phase in RUN_PHASES for u in units_for(phase, records, chosen)]


# ---------------------------------------------------------------- post-run access


def records_from_base(split: str) -> list:
    """manifest_v4.build_manifest without the split guard (same construction)."""

    families = iter(base.assign_families(split))
    records = []
    for width in contract.WIDTHS:
        for depth in contract.DEPTHS:
            for graph_index in range(base.GRAPHS_PER_STRATUM[split]):
                family = next(families)
                edges, attempts = base.draw_graph(
                    split, family, width, depth, graph_index
                )
                records.append(
                    base.GraphRecord(
                        split=split,
                        graph_id=f"{split}-w{width}-p{depth}-g{graph_index}",
                        width=width,
                        depth=depth,
                        graph_index=graph_index,
                        family=family,
                        edges=edges,
                        attempts=attempts,
                        rejected_disconnected=attempts - 1,
                        first_edge=edges[0],
                        first_connected_triple=base.first_connected_triple(
                            width, edges
                        ),
                        candidates=base.draw_candidates(
                            split, width, depth, graph_index
                        ),
                    )
                )
    return records


def records_after_run(repo: Path = REPO) -> list:
    """Holdout manifest for scoring; only after the single run has finalized."""

    split_guard_v4.require_confirmatory_lock(repo)
    if not split_guard_v4.marker_path(repo, SPLIT).is_file():
        raise split_guard_v4.LockError("holdout has not finalized; no marker")
    return records_from_base(SPLIT)


# ---------------------------------------------------------------- finalize


def shard_paths(out: Path, phase: str) -> list[Path]:
    return sorted((out / phase).glob("*.jsonl.gz"))


def check_complete(out: Path, records, chosen) -> dict:
    expected = {tuple(u) for u in all_units(records, chosen)}
    seen, failed, rows, splits = {}, 0, 0, set()
    shards = {}
    for phase in RUN_PHASES:
        for path in shard_paths(out, phase):
            shards[path.relative_to(out).as_posix()] = canonical_sha256(path)
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                for line in handle:
                    entry = json.loads(line)
                    unit = tuple(entry["unit"])
                    seen[unit] = seen.get(unit, 0) + 1
                    if entry["status"] != "ok":
                        failed += 1
                        continue
                    rows += len(entry["rows"])
                    splits |= {r["split"] for r in entry["rows"]}
                    if len(entry["rows"]) != REPEATS:
                        raise RuntimeError(f"unit {unit} has {len(entry['rows'])} rows")
    missing = sorted(expected - set(seen))
    extra = sorted(set(seen) - expected)
    duplicated = sorted(u for u, k in seen.items() if k > 1)
    return {
        "expected_units": len(expected),
        "units_recorded": sum(seen.values()),
        "missing": len(missing),
        "extra": len(extra),
        "duplicated": len(duplicated),
        "failed_units": failed,
        "rows": rows,
        "row_splits": sorted(splits),
        "shards": shards,
        "complete": not missing and not extra and not duplicated and splits <= {SPLIT},
    }


# ---------------------------------------------------------------- reference


def reference_rows(records, chosen):
    cache = execution.SolveCache()
    rows = []
    for r in records:
        for structure in cells_v4.STRUCTURES:
            for point in ("main", "sensitivity"):
                setting = chosen[(structure, point)]
                ref = reference.reference_gap(SPLIT, r, structure, setting, cache)
                rows.append(
                    {
                        "graph_id": r.graph_id,
                        "width": r.width,
                        "depth": r.depth,
                        "structure": structure,
                        "point": point,
                        "setting": setting,
                        "ideal_gap": repr(ref.ideal_gap),
                        "noisy_population_gap": repr(ref.noisy_population_gap),
                        "ideal_tie": int(ref.ideal_tie),
                        "flipped": int(ref.flipped),
                    }
                )
    return rows


# ---------------------------------------------------------------- main


def log_event(out: Path, event: dict) -> None:
    out.mkdir(parents=True, exist_ok=True)
    with (out / "run_log_v4.jsonl").open("a", encoding="utf-8") as h:
        h.write(
            json.dumps(
                {"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **event}, sort_keys=True
            )
            + "\n"
        )


def preflight_run(commit: str) -> None:
    runner.preflight(SPLIT, commit, True)
    dirty = runner._git(
        "status", "--porcelain", "--", "experiments/holdout", "experiments/development"
    )
    if dirty:
        raise runner.RunRefused(f"uncommitted changes in the drivers:\n{dirty}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase", choices=("plan",) + RUN_PHASES + ("finalize", "reference")
    )
    parser.add_argument("--commit", required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    out = args.out
    post = args.phase == "reference"
    try:
        if post:
            records = records_after_run()
        else:
            preflight_run(args.commit)
            records = manifest_v4.build_manifest(SPLIT, REPO)
        chosen = locked_chosen()
    except Exception as error:  # LockError, RunRefused, RuntimeError
        print(f"refused: {error}")
        return 2
    by_id = {r.graph_id: r for r in records}
    protocol_hash = canonical_sha256(REPO / split_guard_v4.PROTOCOL)
    log_event(
        out,
        {
            "event": "start",
            "phase": args.phase,
            "shard": [args.shard_index, args.shard_count],
            "split": SPLIT,
            **dev.environment(args.commit),
        },
    )

    if args.phase == "plan":
        counts = {p: len(units_for(p, records, chosen)) for p in RUN_PHASES}
        print(json.dumps({"graphs": len(records), **counts, "repeats": REPEATS}))
        return 0

    if args.phase in RUN_PHASES:
        selected = dev.shard(
            units_for(args.phase, records, chosen), args.shard_index, args.shard_count
        )
        path = (
            out
            / args.phase
            / f"shard_{args.shard_index:04d}_of_{args.shard_count:04d}.jsonl.gz"
        )
        if path.exists():
            print(f"exists, not rerun: {path}")
            return 0
        summary = dev.write_shard(
            path, selected, by_id, args.commit, protocol_hash, split=SPLIT
        )
        log_event(
            out,
            {
                "event": "done",
                "phase": args.phase,
                "file": path.name,
                "sha256": canonical_sha256(path),
                **summary,
            },
        )
        print(json.dumps({"phase": args.phase, "file": path.name, **summary}))
        return 0

    if args.phase == "finalize":
        report = check_complete(out, records, chosen)
        if not report["complete"]:
            print(json.dumps({k: v for k, v in report.items() if k != "shards"}))
            print("refused: holdout incomplete; marker not written")
            return 2
        marker = split_guard_v4.marker_path(REPO, SPLIT)
        marker.parent.mkdir(parents=True, exist_ok=True)
        payload = {"commit": args.commit, **report}
        with marker.open("x", encoding="utf-8", newline="\n") as h:
            h.write(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        log_event(
            out,
            {
                "event": "done",
                "phase": "finalize",
                "marker_sha256": canonical_sha256(marker),
                **{k: v for k, v in report.items() if k != "shards"},
            },
        )
        print(json.dumps({k: v for k, v in report.items() if k != "shards"}))
        return 0

    # reference, after the marker
    path = out / "reference" / "holdout_reference_v4.csv"
    started = time.perf_counter()
    rows = reference_rows(records, chosen)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    log_event(
        out,
        {
            "event": "done",
            "phase": "reference",
            "rows": len(rows),
            "seconds": time.perf_counter() - started,
            "sha256": canonical_sha256(path),
        },
    )
    print(f"reference rows={len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
