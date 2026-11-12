"""Shared-graph revalidation of the repaired protocol-v2 design.

This is a design simulation, not evidence that a physical probe works.  It
revalidates the already selected 100-graph, 32-repeat design after the matrix
and primary interval changed.  It never constructs a quantum noise model.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import math
import platform
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np


ROOT_SEED = 20261111
GRAPH_COUNT = 100
REPEATS = 32
STRATA = 25
GRAPHS_PER_STRATUM = 4
DATASET_SIMULATIONS = 250
BOOTSTRAP_RESAMPLES = 1_000
VISIBLE_THRESHOLD = 0.80
BLIND_CEILING = 0.10
FALSE_ALARM_CEILING = 0.10
PRIMARY_LOWER_THRESHOLD = 0.80
MATRIX_SHA256 = "7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995"
PRIMARY_PROBES = {"P0", "P1", "P2", "P3", "P4a", "P4b", "P5"}
EXPECTED_COUNTS = Counter({"blind": 35, "partial": 15, "visible": 6})

# The shared shift is deliberately nonzero so all cells reuse a graph-level
# difficulty factor.  Scales are fractions of min(p,1-p), which preserves the
# marginal mean without clipping.
SHARED_GRAPH_SCALE = 0.20
CELL_GRAPH_SCALE = 0.30

SCENARIOS = (
    {
        "name": "baseline",
        "visible_mean": 0.85,
        "partial_mean": 0.45,
        "blind_mean": 0.05,
        "false_alarm_mean": 0.05,
        "target": 0.90,
    },
    {
        "name": "lower_boundary_stress",
        "visible_mean": 0.82,
        "partial_mean": 0.12,
        "blind_mean": 0.08,
        "false_alarm_mean": 0.08,
        "target": 0.80,
    },
    {
        "name": "upper_boundary_stress",
        "visible_mean": 0.82,
        "partial_mean": 0.78,
        "blind_mean": 0.08,
        "false_alarm_mean": 0.08,
        "target": 0.80,
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", type=Path, default=Path("docs/theory/06_matrix.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("experiments/power"))
    parser.add_argument("--matrix-committed-confirmed", action="store_true")
    return parser.parse_args()


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    radius = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total + z * z / (4 * total * total)
        )
        / denominator
    )
    return centre - radius, centre + radius


def load_labels(path: Path) -> tuple[np.ndarray, str]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != MATRIX_SHA256:
        raise ValueError(f"matrix hash mismatch: {digest}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    labels = [row["prediction"] for row in rows if row["probe"] in PRIMARY_PROBES]
    if Counter(labels) != EXPECTED_COUNTS or len(labels) != 56:
        raise ValueError(f"matrix label mismatch: {Counter(labels)}")
    return np.asarray(labels), digest


def graph_rates(
    rng: np.random.Generator,
    means: np.ndarray,
    shared_uniform: np.ndarray,
) -> np.ndarray:
    graph_count = shared_uniform.size
    cell_uniform = rng.uniform(-1.0, 1.0, size=(graph_count, means.size))
    room = np.minimum(means, 1.0 - means)
    probabilities = (
        means[None, :]
        + SHARED_GRAPH_SCALE * room[None, :] * shared_uniform[:, None]
        + CELL_GRAPH_SCALE * room[None, :] * cell_uniform
    )
    if np.any((probabilities < 0) | (probabilities > 1)):
        raise AssertionError("hierarchical probabilities left [0,1]")
    return rng.binomial(REPEATS, probabilities) / REPEATS


def stratified_bootstrap_weights(
    rng: np.random.Generator, resamples: int = BOOTSTRAP_RESAMPLES
) -> np.ndarray:
    if STRATA * GRAPHS_PER_STRATUM != GRAPH_COUNT:
        raise AssertionError("strata do not cover graphs")
    weights = np.zeros((resamples, GRAPH_COUNT), dtype=np.uint8)
    rows = np.arange(resamples)
    for stratum in range(STRATA):
        start = stratum * GRAPHS_PER_STRATUM
        draws = rng.integers(
            start,
            start + GRAPHS_PER_STRATUM,
            size=(resamples, GRAPHS_PER_STRATUM),
        )
        for column in range(GRAPHS_PER_STRATUM):
            np.add.at(weights, (rows, draws[:, column]), 1)
    return weights


def observed_labels(power: np.ndarray, false_alarm: np.ndarray) -> np.ndarray:
    visible = (power >= VISIBLE_THRESHOLD) & (false_alarm <= FALSE_ALARM_CEILING)
    blind = (~visible) & (power <= BLIND_CEILING)
    return np.where(visible, "visible", np.where(blind, "blind", "partial"))


def simulate_dataset(
    rng: np.random.Generator,
    labels: np.ndarray,
    scenario: dict[str, float | str],
) -> tuple[float, float, float]:
    means = np.asarray([float(scenario[f"{label}_mean"]) for label in labels])
    false_means = np.full(labels.size, float(scenario["false_alarm_mean"]))
    shared_detection = rng.uniform(-1.0, 1.0, size=GRAPH_COUNT)
    shared_false_alarm = rng.uniform(-1.0, 1.0, size=GRAPH_COUNT)
    detection = graph_rates(rng, means, shared_detection)
    false_alarm = graph_rates(rng, false_means, shared_false_alarm)

    point_labels = observed_labels(detection.mean(axis=0), false_alarm.mean(axis=0))
    point = float(np.mean(point_labels == labels))

    weights = stratified_bootstrap_weights(rng)
    denominator = STRATA * GRAPHS_PER_STRATUM
    boot_power = weights @ detection / denominator
    boot_false_alarm = weights @ false_alarm / denominator
    boot_labels = observed_labels(boot_power, boot_false_alarm)
    boot_agreement = np.mean(boot_labels == labels[None, :], axis=1)
    lower, upper = np.quantile(
        boot_agreement, (0.025, 0.975), method="inverted_cdf"
    )
    return point, float(lower), float(upper)


def write_csv_exclusive(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    if not args.matrix_committed_confirmed:
        raise SystemExit(
            "Refusing to run: owner must first confirm the repaired matrix is committed."
        )
    labels, matrix_hash = load_labels(args.matrix)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "power_analysis_raw_v4.csv"
    summary_path = output_dir / "power_analysis_summary_v4.csv"
    log_path = output_dir / "run_log_v4.txt"
    for path in (raw_path, summary_path, log_path):
        if path.exists():
            raise SystemExit(f"Refusing to overwrite existing output: {path}")

    start = time.time()
    raw_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    for scenario_index, scenario in enumerate(SCENARIOS):
        rng = np.random.default_rng(
            np.random.SeedSequence([ROOT_SEED, 4, scenario_index, GRAPH_COUNT, REPEATS])
        )
        successes = 0
        for dataset_index in range(DATASET_SIMULATIONS):
            point, lower, upper = simulate_dataset(rng, labels, scenario)
            success = int(lower >= PRIMARY_LOWER_THRESHOLD)
            successes += success
            raw_rows.append(
                {
                    "scenario": scenario["name"],
                    "dataset_index": dataset_index,
                    "graph_count": GRAPH_COUNT,
                    "repeats_per_graph": REPEATS,
                    "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
                    "agreement_point": point,
                    "agreement_bootstrap_lower": lower,
                    "agreement_bootstrap_upper": upper,
                    "primary_success": success,
                }
            )
        power = successes / DATASET_SIMULATIONS
        power_lower, power_upper = wilson_interval(successes, DATASET_SIMULATIONS)
        target = float(scenario["target"])
        summary_rows.append(
            {
                "scenario": scenario["name"],
                "dataset_simulations": DATASET_SIMULATIONS,
                "estimated_design_power": power,
                "power_wilson_lower": power_lower,
                "power_wilson_upper": power_upper,
                "power_target": target,
                "point_margin_from_target": power - target,
                "lower_margin_from_target": power_lower - target,
                "passes_point_target": int(power >= target),
                "passes_lower_target": int(power_lower >= target),
            }
        )

    write_csv_exclusive(raw_path, raw_rows)
    write_csv_exclusive(summary_path, summary_rows)
    config = io.StringIO()
    with contextlib.redirect_stdout(config):
        np.show_config()
    with log_path.open("x", encoding="utf-8") as handle:
        handle.write("Power analysis v4 run log\n")
        handle.write(f"command={' '.join(sys.argv)}\n")
        handle.write("matrix_commit_confirmation=user supplied; Git history not inspected\n")
        handle.write(f"matrix_sha256={matrix_hash}\n")
        handle.write(f"class_counts={dict(Counter(labels))}\n")
        handle.write(f"root_seed={ROOT_SEED}\n")
        handle.write(f"graph_count={GRAPH_COUNT}\n")
        handle.write(f"repeats={REPEATS}\n")
        handle.write(f"dataset_simulations={DATASET_SIMULATIONS}\n")
        handle.write(f"bootstrap_resamples={BOOTSTRAP_RESAMPLES}\n")
        handle.write(f"shared_graph_scale={SHARED_GRAPH_SCALE}\n")
        handle.write(f"cell_graph_scale={CELL_GRAPH_SCALE}\n")
        handle.write(f"scenarios={SCENARIOS}\n")
        handle.write(f"python={sys.version}\n")
        handle.write(f"platform={platform.platform()}\n")
        handle.write(f"numpy={np.__version__}\n")
        handle.write(f"elapsed_seconds={time.time() - start:.6f}\n")
        handle.write("\nnp.show_config()\n")
        handle.write(config.getvalue())

    for row in summary_rows:
        print(
            f"{row['scenario']}: power={row['estimated_design_power']:.4f}, "
            f"lower={row['power_wilson_lower']:.4f}, target={row['power_target']:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

