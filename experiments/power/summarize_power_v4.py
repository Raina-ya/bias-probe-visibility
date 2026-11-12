"""Independently recompute the power-v4 scenario summary from raw rows."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


TARGETS = {
    "baseline": 0.90,
    "lower_boundary_stress": 0.80,
    "upper_boundary_stress": 0.80,
}


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    radius = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return centre - radius, centre + radius


def summarize(path: Path) -> list[dict[str, float | int | str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            groups[row["scenario"]].append(row)

    summaries: list[dict[str, float | int | str]] = []
    for scenario in TARGETS:
        rows = groups[scenario]
        successes = sum(int(row["primary_success"]) for row in rows)
        total = len(rows)
        lower, upper = wilson_interval(successes, total)
        power = successes / total
        summaries.append(
            {
                "scenario": scenario,
                "datasets": total,
                "successes": successes,
                "power": power,
                "wilson_lower": lower,
                "wilson_upper": upper,
                "target": TARGETS[scenario],
                "lower_margin": lower - TARGETS[scenario],
                "minimum_endpoint_lower": min(
                    float(row["agreement_bootstrap_lower"]) for row in rows
                ),
            }
        )
    return summaries


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    for row in summarize(root / "experiments" / "power" / "power_analysis_raw_v4.csv"):
        print(
            f"{row['scenario']}: {row['successes']}/{row['datasets']}, "
            f"power={row['power']:.4f}, lower={row['wilson_lower']:.4f}, "
            f"target={row['target']:.2f}, margin={row['lower_margin']:+.4f}, "
            f"min_endpoint_lower={row['minimum_endpoint_lower']:.4f}"
        )


if __name__ == "__main__":
    main()

