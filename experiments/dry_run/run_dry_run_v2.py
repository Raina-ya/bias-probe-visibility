"""Outcome-free dry-run ledger for protocol v2, Sections 6.1, 6.2, and 12.

For every primary probe, width, and probe fraction it lists the circuits and
their shot allocation and checks that target plus probe shots equal the fixed
total.  It also recomputes the Section 12 resource upper bound.  No circuit is
built or simulated and no seed is instantiated.
"""

from __future__ import annotations

import argparse
import csv
import math
import platform
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import protocol_contract as contract  # noqa: E402

FRACTIONS = (0.05, 0.10, 0.25)
SECTION12 = {
    "graphs": 150,
    "parameter_conditions": 60,
    "aggregate_rows": 2_016_000,
    "nominal_shots": 33_030_144_000,
    "unique_probability_solves": 1_231_200,
    "projected_raw_bytes": 16_389_242_880,
}
FIELDS = (
    "probe",
    "width",
    "fraction",
    "target_shots",
    "probe_shots",
    "target_circuits",
    "probe_circuits",
    "min_shots_per_probe_circuit",
    "max_shots_per_probe_circuit",
    "budget_conserved",
)


def probe_circuits(probe: str, width: int) -> list[str]:
    if probe in {"P0", "P5"}:
        return []
    if probe == "P1":
        return ["A_s3", "B_s3"]
    if probe == "P2":
        return ["A_twin", "B_twin"]
    if probe == "P3":
        return [f"{c}_frame{h}" for c in "AB" for h in range(16)]
    if probe == "P4a":
        return ["prep0", "prep1"]
    if probe == "P4b":
        return [
            f"pair{i}{j}_prep{a}{b}"
            for i in range(width)
            for j in range(i + 1, width)
            for a in (0, 1)
            for b in (0, 1)
        ]
    raise ValueError(probe)


def ledger_row(probe: str, width: int, fraction: float) -> dict[str, object]:
    total = contract.TOTAL_SHOTS
    circuits = probe_circuits(probe, width)
    n_probe = math.floor(fraction * total) if circuits else 0
    n_target = total - n_probe
    target = contract.split_even(n_target, ["A", "B"])
    probes = contract.split_even(n_probe, circuits) if circuits else {}
    conserved = sum(target.values()) + sum(probes.values()) == total
    return {
        "probe": probe,
        "width": width,
        "fraction": fraction if circuits else 0.0,
        "target_shots": n_target,
        "probe_shots": n_probe,
        "target_circuits": 2,
        "probe_circuits": len(circuits),
        "min_shots_per_probe_circuit": min(probes.values()) if probes else 0,
        "max_shots_per_probe_circuit": max(probes.values()) if probes else 0,
        "budget_conserved": int(conserved),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path, default=REPO / "experiments" / "dry_run"
    )
    args = parser.parse_args()
    ledger_path = args.output_dir / "dry_run_ledger_v2.csv"
    log_path = args.output_dir / "dry_run_log_v2.txt"
    for path in (ledger_path, log_path):
        if path.exists():
            print(f"Refusing to overwrite existing output: {path}")
            return 1

    rows = []
    for probe in contract.PRIMARY_PROBES:
        for width in contract.WIDTHS:
            fractions = FRACTIONS if probe_circuits(probe, width) else (0.0,)
            for fraction in fractions:
                rows.append(ledger_row(probe, width, fraction))
    failures = [row for row in rows if not row["budget_conserved"]]

    estimate = contract.estimate_resources().to_dict()
    mismatches = {
        key: (estimate[key], expected)
        for key, expected in SECTION12.items()
        if estimate[key] != expected
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    status = (
        "PASS"
        if not failures and not mismatches and estimate["within_structural_caps"]
        else "FAIL"
    )
    lines = [
        "Dry-run ledger v2 (outcome-free; no circuit built, no seed instantiated)",
        f"ledger_rows={len(rows)}",
        f"budget_failures={len(failures)}",
        f"section12_mismatches={mismatches}",
        *(f"{key}={value}" for key, value in estimate.items()),
        f"python={sys.version.split()[0]}",
        f"platform={platform.platform()}",
        f"numpy={np.__version__}",
        f"dry_run_status={status}",
    ]
    with log_path.open("x", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
