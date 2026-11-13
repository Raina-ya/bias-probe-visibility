"""Project full development elapsed time from the 1% timing pilot.

Each pilot unit's elapsed seconds are averaged within (probe, structure kind,
width, depth) cells, where the structure kind is the structure code and null
or main; every full unit is assigned its cell mean (falling back to the
(probe, structure, width) mean, then the probe mean).  The projection is
compared with the 14-day cap of protocol v3/v4 Section 12.
"""

from __future__ import annotations

import argparse
import gzip
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "experiments" / "development"))
sys.path.insert(0, str(REPO / "src"))

import run_development_v4 as dev  # noqa: E402

CAP_SECONDS = 14 * 24 * 3600


def width_depth(graph_id: str) -> tuple[int, int]:
    parts = graph_id.split("-")
    return int(parts[1][1:]), int(parts[2][1:])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=dev.OUT)
    args = parser.parse_args()
    times = defaultdict(list)
    failed = 0
    for path in sorted((args.out / "pilot").glob("*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as h:
            for line in h:
                e = json.loads(line)
                if e["status"] != "ok":
                    failed += 1
                    continue
                _, probe, structure, _, _, graph_id = e["unit"]
                w, d = width_depth(graph_id)
                times[(probe, structure, w, d)].append(e["seconds"])
    if not times:
        print("no pilot shards found")
        return 1
    import manifest_v4

    records = manifest_v4.build_manifest(dev.SPLIT, REPO)
    chosen = dev.read_chosen(args.out / "strength_map_v4.csv")
    full = dev.null_units(records) + dev.main_units(records, chosen)
    by_pw, by_p = defaultdict(list), defaultdict(list)
    for (p, s, w, _d), v in times.items():
        by_pw[(p, s, w)] += v
        by_p[p] += v
    total = 0.0
    for _, probe, structure, _, _, graph_id in full:
        w, d = width_depth(graph_id)
        v = (
            times.get((probe, structure, w, d))
            or by_pw.get((probe, structure, w))
            or by_p.get(probe)
        )
        total += (
            statistics.mean(v)
            if v
            else statistics.mean([x for vs in times.values() for x in vs])
        )
    pilot_seconds = sum(sum(v) for v in times.values())
    result = {
        "pilot_units_ok": sum(len(v) for v in times.values()),
        "pilot_units_failed": failed,
        "pilot_seconds": round(pilot_seconds, 1),
        "full_units": len(full),
        "projected_seconds_single_process": round(total, 1),
        "projected_days_single_process": round(total / 86400, 3),
        "cap_days": 14,
        "within_cap_single_process": total <= CAP_SECONDS,
    }
    print(json.dumps(result, indent=1))
    with (args.out / "timing_projection_v4.json").open("x", encoding="utf-8") as h:
        h.write(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
