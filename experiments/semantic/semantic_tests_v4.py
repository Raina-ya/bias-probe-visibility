"""Population-level semantic tests of the v4 matrix strata (split 99 only).

Evidence type: exact population computation (expected counts, no shots) on the
software-test namespace.  For every v4 cell it compares the cell's component
statistic at the structure's strongest settings with its value at the matched
null.  A cell is observed *invariant* when every difference is below 1e-9 on
every graph, and *sensitive* otherwise.  This checks the analytic direction
(invariant versus sensitive) only; it says nothing about budget-limited power,
so it cannot confirm a visible or partial label.
"""

from __future__ import annotations

import argparse
import csv
import platform
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import cells_v4  # noqa: E402
import execution  # noqa: E402
import manifest  # noqa: E402

STRONGEST = {
    "E1": ["0.04"],
    "E2": ["-0.04", "0.04"],
    "E3": ["-0.04", "0.04"],
    "E4": ["(0.08,0.12)", "(0.12,0.08)"],
    "E5": ["-0.01", "0.01"],
    "E5'": ["-0.015625", "0.015625"],
    "E6": ["-0.03", "0.03"],
}
TOL = 1e-9


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graphs", type=int, default=10)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "experiments" / "semantic" / "semantic_tests_v4.csv",
    )
    args = parser.parse_args()
    if args.output.exists():
        print(f"Refusing to overwrite existing output: {args.output}")
        return 1
    records = [
        r for r in manifest.build_manifest("software_test", REPO) if r.width <= 6
    ][::3][: args.graphs]
    matrix = cells_v4.load_matrix()
    cache = execution.SolveCache()
    rows = []
    for probe, structure in cells_v4.cells():
        diffs = []
        for record in records:

            def value(setting, record=record, probe=probe, structure=structure):
                row = execution.run_row(
                    split="software_test",
                    record=record,
                    probe=probe,
                    structure=structure,
                    setting=setting,
                    parameter_index=0,
                    repeat=0,
                    cache=cache,
                    population=True,
                )
                return cells_v4.cell_value(row, probe, structure)

            null = value(cells_v4.MATCHED_NULL[structure])
            diffs += [abs(value(s) - null) for s in STRONGEST[structure]]
        observed = "invariant" if max(diffs) < TOL else "sensitive"
        expected = matrix[(probe, structure)]["stratum"]
        rows.append(
            {
                "probe": probe,
                "structure": structure,
                "component": cells_v4.component(probe, structure),
                "expected_stratum": expected,
                "observed_stratum": observed,
                "max_abs_difference": repr(float(max(diffs))),
                "median_abs_difference": repr(float(np.median(diffs))),
                "agrees": int(observed == expected),
            }
        )
        print(probe, structure, expected, observed, f"{max(diffs):.3e}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    log = args.output.with_name(args.output.stem + "_log.txt")
    with log.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(
            f"graphs={len(records)} cells={len(rows)} disagreements={sum(1 - r['agrees'] for r in rows)}\n"
            f"python={sys.version.split()[0]}\nplatform={platform.platform()}\nnumpy={np.__version__}\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
