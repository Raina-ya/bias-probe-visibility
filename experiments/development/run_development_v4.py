"""Development (split 10) driver for protocol v4, Task 2-2.

Phases, run in this order on the reference workstation:

  reference     exact ideal and noisy population gaps for every structure and grid
                setting (no shots); input of the Section 4.2 strength map
  strength-map  writes strength_map_v4.csv from the reference rows
  pilot         1% timing pilot: every 100th work unit of the null and main phases
  nulls         E0 (7 offsets) and every structure's matched null, all probes
  main          every probe at every structure's main operating point

A work unit is one (probe, structure, setting, parameter index, graph) with 32
repeats.  Units are enumerated in a frozen canonical order and split into
shards; each shard is written once to a gzip JSONL file opened exclusively, so
nothing is ever overwritten and an interrupted run resumes by skipping
finished shards.  Failed units are written to the same file with their error.

The driver only ever builds the development manifest through manifest_v4,
which the v4 lock admits.  It never builds or reads a holdout manifest.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import platform
import sys
import time
import traceback
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import cells_v4  # noqa: E402
import channels  # noqa: E402
import execution  # noqa: E402
import manifest_v4  # noqa: E402
import reference  # noqa: E402
import runner  # noqa: E402
import strength_map  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

SPLIT = "development"
REPEATS = 32
PROBES = ("P0", "P1", "P2", "P3", "P4a", "P4b", "P5")
NULL_PROBES = (
    "P1",
    "P2",
    "P3",
    "P4a",
    "P4b",
    "P5",
)  # matched nulls calibrate bias probes
PILOT_STRIDE = 100
OUT = REPO / "results" / "development_v4"


# ---------------------------------------------------------------- work units


def setting_index(structure: str, setting: str) -> int:
    labels = [label for label, _ in strength_map.GRIDS[structure]]
    return labels.index(setting)


def null_units(records):
    units = []
    for probe in PROBES:
        for k, value in enumerate(channels.E0_VALUES):
            for r in records:
                units.append(("nulls", probe, "E0", repr(value), k, r.graph_id))
    for probe in NULL_PROBES:
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


def main_units(records, chosen):
    units = []
    for probe in PROBES:
        for structure in cells_v4.STRUCTURES:
            setting = chosen[(structure, "main")]
            for r in records:
                units.append(
                    (
                        "main",
                        probe,
                        structure,
                        setting,
                        setting_index(structure, setting),
                        r.graph_id,
                    )
                )
    return units


def pilot_units(records, chosen):
    everything = null_units(records) + main_units(records, chosen)
    return [("pilot",) + u[1:] for u in everything[::PILOT_STRIDE]]


def shard(units, index, count):
    return [u for k, u in enumerate(units) if k % count == index]


# ---------------------------------------------------------------- execution


def run_unit(unit, records_by_id, commit, protocol_hash, cache, split=SPLIT):
    _, probe, structure, setting, parameter_index, graph_id = unit
    record = records_by_id[graph_id]
    started = time.perf_counter()
    rows = []
    for repeat in range(REPEATS):
        row = execution.run_row(
            split=split,
            record=record,
            probe=probe,
            structure=structure,
            setting=setting,
            parameter_index=parameter_index,
            repeat=repeat,
            cache=cache,
            commit=commit,
            protocol_sha256=protocol_hash,
        )
        rows.append(runner.row_json(row))
    return rows, time.perf_counter() - started


def write_shard(
    path: Path, units, records_by_id, commit, protocol_hash, split=SPLIT
) -> dict:
    cache = execution.SolveCache()
    summary = {"units": 0, "failed": 0, "seconds": 0.0}
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as gz:
        for unit in units:
            entry = {"unit": list(unit)}
            try:
                rows, seconds = run_unit(
                    unit, records_by_id, commit, protocol_hash, cache, split
                )
                entry.update(
                    status="ok", seconds=seconds, rows=[json.loads(r) for r in rows]
                )
                summary["seconds"] += seconds
            except Exception:  # failed units are kept, never dropped
                entry.update(status="failed", error=traceback.format_exc())
                summary["failed"] += 1
            summary["units"] += 1
            gz.write((json.dumps(entry, sort_keys=True) + "\n").encode("utf-8"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(buffer.getvalue())
    return summary


def reference_rows(records):
    cache = execution.SolveCache()
    rows = []
    for r in records:
        for structure, grid in strength_map.GRIDS.items():
            for label, _ in grid:
                ref = reference.reference_gap(SPLIT, r, structure, label, cache)
                rows.append(
                    {
                        "graph_id": r.graph_id,
                        "width": r.width,
                        "depth": r.depth,
                        "structure": structure,
                        "setting": label,
                        "ideal_gap": repr(ref.ideal_gap),
                        "noisy_population_gap": repr(ref.noisy_population_gap),
                        "ideal_tie": int(ref.ideal_tie),
                        "harmful_ratio": repr(float(ref.harmful_ratio)),
                        "flipped": int(ref.flipped),
                    }
                )
    return rows


def read_reference(path: Path):
    with path.open(encoding="utf-8", newline="") as h:
        return [
            strength_map.ReferenceRow(
                r["structure"],
                r["setting"],
                r["graph_id"],
                float(r["harmful_ratio"]),
                r["ideal_tie"] == "1",
            )
            for r in csv.DictReader(h)
        ]


def read_chosen(path: Path):
    with path.open(encoding="utf-8", newline="") as h:
        return {
            (r["structure"], r["point"]): r["setting"]
            for r in csv.DictReader(h)
            if r["chosen"] == "1"
        }


def environment(commit: str) -> dict:
    import qiskit
    import scipy

    return {
        "commit": commit,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "qiskit": qiskit.__version__,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase", choices=("reference", "strength-map", "pilot", "nulls", "main", "plan")
    )
    parser.add_argument("--commit", required=True)
    parser.add_argument("--previous-project-closed", action="store_true")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    try:
        runner.preflight(SPLIT, args.commit, args.previous_project_closed)
        dirty = runner._git("status", "--porcelain", "--", "experiments/development")
        if dirty:
            raise runner.RunRefused(
                f"uncommitted changes in the development driver:\n{dirty}"
            )
    except Exception as error:  # LockError or RunRefused
        print(f"refused: {error}")
        return 2
    records = manifest_v4.build_manifest(SPLIT, REPO)
    by_id = {r.graph_id: r for r in records}
    protocol_hash = canonical_sha256(REPO / "docs/freeze/frozen_protocol_v4.md")
    out = args.out
    ref_path = out / "reference" / "dev_reference_v4.csv"
    map_path = out / "strength_map_v4.csv"
    log_path = out / "run_log_v4.jsonl"

    def log(event: dict) -> None:
        out.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as h:
            h.write(
                json.dumps(
                    {"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), **event},
                    sort_keys=True,
                )
                + "\n"
            )

    log(
        {
            "event": "start",
            "phase": args.phase,
            "shard": [args.shard_index, args.shard_count],
            **environment(args.commit),
        }
    )

    if args.phase == "reference":
        if ref_path.exists():
            print(f"exists, not overwritten: {ref_path}")
            return 0
        started = time.perf_counter()
        rows = reference_rows(records)
        ref_path.parent.mkdir(parents=True, exist_ok=True)
        with ref_path.open("x", encoding="utf-8", newline="") as h:
            w = csv.DictWriter(h, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        log(
            {
                "event": "done",
                "phase": "reference",
                "rows": len(rows),
                "seconds": time.perf_counter() - started,
            }
        )
        print(f"reference rows={len(rows)}")
        return 0

    if args.phase == "strength-map":
        if map_path.exists():
            print(f"exists, not overwritten: {map_path}")
            return 0
        text = strength_map.render_csv(
            strength_map.choose(read_reference(ref_path)), canonical_sha256(ref_path)
        )
        with map_path.open("x", encoding="utf-8", newline="\n") as h:
            h.write(text)
        log(
            {
                "event": "done",
                "phase": "strength-map",
                "input_sha256": canonical_sha256(ref_path),
            }
        )
        print(f"wrote {map_path}")
        return 0

    chosen = read_chosen(map_path)
    if args.phase == "plan":
        n, m, p = (
            len(null_units(records)),
            len(main_units(records, chosen)),
            len(pilot_units(records, chosen)),
        )
        print(
            json.dumps(
                {
                    "null_units": n,
                    "main_units": m,
                    "pilot_units": p,
                    "repeats": REPEATS,
                    "rows": (n + m) * REPEATS,
                }
            )
        )
        return 0

    if args.phase == "pilot":
        selected = pilot_units(records, chosen)
    elif args.phase == "nulls":
        selected = null_units(records)
    else:
        selected = main_units(records, chosen)
    mine = shard(selected, args.shard_index, args.shard_count)
    path = (
        out
        / args.phase
        / f"shard_{args.shard_index:04d}_of_{args.shard_count:04d}.jsonl.gz"
    )
    if path.exists():
        print(f"exists, not overwritten: {path}")
        return 0
    summary = write_shard(path, mine, by_id, args.commit, protocol_hash)
    log(
        {
            "event": "done",
            "phase": args.phase,
            "file": path.name,
            "sha256": canonical_sha256(path),
            **summary,
        }
    )
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
