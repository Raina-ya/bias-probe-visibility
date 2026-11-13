"""Compare a rebuilt development reference and strength map with the committed ones.

Used by the CI rebuild workflow (Linux and Windows).  No tolerance is applied:
every difference is reported as a finding (spec item 38), with the number of
rows that differ, the largest absolute difference per numeric column, and the
smallest distance of any committed value from the decision thresholds it
feeds (zero for ideal ties, the tie tolerance 1e-12 for development medians).

Exit status 1 only if a decision changes: a different set of rows, an
ideal-tie or flipped flag, or a chosen strength-map setting.  Floating-point
differences that change no decision exit 0 and are listed in the report.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REFERENCE = "reference/dev_reference_v4.csv"
STRENGTH_MAP = "strength_map_v4.csv"
REF_KEY = ("graph_id", "structure", "setting")
REF_FLOATS = ("ideal_gap", "noisy_population_gap", "harmful_ratio")
REF_FLAGS = ("ideal_tie", "flipped")
MAP_KEY = ("structure", "point", "setting")
TIE_TOLERANCE = 1e-12


def _rows(path: Path, key) -> dict:
    with path.open(encoding="utf-8", newline="") as h:
        return {tuple(r[k] for k in key): r for r in csv.DictReader(h)}


def compare(committed: Path, rebuilt: Path) -> dict:
    a, b = _rows(committed / REFERENCE, REF_KEY), _rows(rebuilt / REFERENCE, REF_KEY)
    report = {
        "reference_rows": [len(a), len(b)],
        "reference_keys_only_committed": len(a.keys() - b.keys()),
        "reference_keys_only_rebuilt": len(b.keys() - a.keys()),
        "reference_columns": {},
    }
    common = sorted(a.keys() & b.keys())
    for col in REF_FLOATS:
        diffs = [abs(float(a[k][col]) - float(b[k][col])) for k in common]
        report["reference_columns"][col] = {
            "rows_differing": sum(d != 0.0 for d in diffs),
            "max_abs_difference": max(diffs, default=0.0),
        }
    for col in REF_FLAGS:
        report["reference_columns"][col] = {
            "rows_differing": sum(a[k][col] != b[k][col] for k in common)
        }
    report["closest_ideal_gap_to_zero"] = min(
        (abs(float(a[k]["ideal_gap"])) for k in common), default=None
    )

    ma, mb = (
        _rows(committed / STRENGTH_MAP, MAP_KEY),
        _rows(rebuilt / STRENGTH_MAP, MAP_KEY),
    )
    chosen_a = {k for k, r in ma.items() if r["chosen"] == "1"}
    chosen_b = {k for k, r in mb.items() if r["chosen"] == "1"}
    medians = [
        abs(float(ma[k]["development_median"]) - float(mb[k]["development_median"]))
        for k in ma.keys() & mb.keys()
        if ma[k]["development_median"] and mb[k]["development_median"]
    ]
    report["strength_map"] = {
        "rows": [len(ma), len(mb)],
        "chosen_equal": chosen_a == chosen_b,
        "median_rows_differing": sum(d != 0.0 for d in medians),
        "median_max_abs_difference": max(medians, default=0.0),
        "closest_median_to_tie_tolerance": min(
            (
                abs(abs(float(r["development_median"])) - TIE_TOLERANCE)
                for r in ma.values()
                if r["development_median"]
            ),
            default=None,
        ),
    }
    report["decision_changed"] = bool(
        report["reference_keys_only_committed"]
        or report["reference_keys_only_rebuilt"]
        or any(report["reference_columns"][c]["rows_differing"] for c in REF_FLAGS)
        or not report["strength_map"]["chosen_equal"]
    )
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("committed", type=Path)
    parser.add_argument("rebuilt", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    report = compare(args.committed, args.rebuilt)
    text = json.dumps(report, indent=1, sort_keys=True)
    print(text)
    if args.report:
        args.report.write_text(text + "\n", encoding="utf-8")
    return 1 if report["decision_changed"] else 0


if __name__ == "__main__":
    sys.exit(main())
