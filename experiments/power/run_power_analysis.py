"""Simulation-based power analysis for the frozen visibility matrix.

The screen uses the normal approximation to a beta-binomial mean.  The first
screened design that meets all power targets is then checked with direct
beta-binomial simulation.  Every random stream is derived from ROOT_SEED.
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
SCREEN_SIMULATIONS = 5_000
EXACT_SIMULATIONS = 5_000
GRAPH_COUNTS = (50, 75, 100)
REPEAT_COUNTS = (1, 2, 4, 8, 16, 32, 64)
WIDTHS = (4, 5, 6, 7, 8)
DEPTHS = (1, 2, 3, 4, 5)
GRAPH_FAMILIES = (
    "Erdos-Renyi",
    "Watts-Strogatz",
    "Barabasi-Albert",
)

VISIBLE_THRESHOLD = 0.80
ALARM_ALPHA = 0.05
BLIND_CEILING = ALARM_ALPHA + 0.05
FALSE_ALARM_CEILING = 0.10
PRIMARY_SUCCESS_THRESHOLD = 0.80
BASELINE_POWER_TARGET = 0.90
STRESS_POWER_TARGET = 0.80
INTRACLASS_CORRELATION = 0.10

SCENARIOS = (
    {
        "name": "baseline",
        "visible_mean": 0.85,
        "partial_mean": 0.45,
        "blind_mean": 0.05,
        "false_alarm_mean": 0.05,
        "target": BASELINE_POWER_TARGET,
    },
    {
        "name": "lower_boundary_stress",
        "visible_mean": 0.82,
        "partial_mean": 0.12,
        "blind_mean": 0.08,
        "false_alarm_mean": 0.08,
        "target": STRESS_POWER_TARGET,
    },
    {
        "name": "upper_boundary_stress",
        "visible_mean": 0.82,
        "partial_mean": 0.78,
        "blind_mean": 0.08,
        "false_alarm_mean": 0.08,
        "target": STRESS_POWER_TARGET,
    },
)

PRIMARY_EXCLUDED_PROBES = {"P1b", "GVS"}
EVALUABLE_LABELS = {"visible", "partial", "blind"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--matrix",
        type=Path,
        default=Path("docs/theory/06_matrix.csv"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("experiments/power"),
    )
    parser.add_argument(
        "--matrix-committed-confirmed",
        action="store_true",
        help="Required human confirmation; this script does not inspect Git history.",
    )
    parser.add_argument(
        "--run-label",
        default="",
        help="Optional filename suffix for a new immutable run, for example v2.",
    )
    parser.add_argument(
        "--selection-basis",
        choices=("point", "lower"),
        default="point",
        help="Use the power point estimate or its 95% Wilson lower bound.",
    )
    return parser.parse_args()


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    proportion = successes / total
    denominator = 1.0 + z * z / total
    centre = (proportion + z * z / (2.0 * total)) / denominator
    radius = (
        z
        * math.sqrt(
            proportion * (1.0 - proportion) / total
            + z * z / (4.0 * total * total)
        )
        / denominator
    )
    return centre - radius, centre + radius


def minimum_agreements_for_success(total_cells: int) -> int:
    for agreements in range(total_cells + 1):
        lower, _ = wilson_interval(agreements, total_cells)
        if lower >= PRIMARY_SUCCESS_THRESHOLD:
            return agreements
    raise RuntimeError("No attainable agreement count reaches the success threshold")


def load_matrix(path: Path) -> tuple[Counter[str], list[dict[str, str]], str]:
    matrix_bytes = path.read_bytes()
    matrix_hash = hashlib.sha256(matrix_bytes).hexdigest()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    primary_rows = [row for row in rows if row["probe"] not in PRIMARY_EXCLUDED_PROBES]
    unresolved = [row for row in primary_rows if row["prediction"] not in EVALUABLE_LABELS]
    evaluable = [row for row in primary_rows if row["prediction"] in EVALUABLE_LABELS]
    return Counter(row["prediction"] for row in evaluable), unresolved, matrix_hash


def seed_for(stage: int, scenario_index: int, graph_count: int, repeats: int) -> np.random.SeedSequence:
    return np.random.SeedSequence(
        [ROOT_SEED, stage, scenario_index, graph_count, repeats]
    )


def normal_estimates(
    rng: np.random.Generator,
    mean: float,
    graph_count: int,
    repeats: int,
    shape: tuple[int, int],
) -> np.ndarray:
    variance = (
        mean
        * (1.0 - mean)
        * (1.0 + (repeats - 1) * INTRACLASS_CORRELATION)
        / (graph_count * repeats)
    )
    return np.clip(rng.normal(mean, math.sqrt(variance), size=shape), 0.0, 1.0)


def exact_estimates(
    rng: np.random.Generator,
    mean: float,
    graph_count: int,
    repeats: int,
    shape: tuple[int, int],
) -> np.ndarray:
    concentration = 1.0 / INTRACLASS_CORRELATION - 1.0
    alpha = mean * concentration
    beta = (1.0 - mean) * concentration
    graph_probabilities = rng.beta(alpha, beta, size=(*shape, graph_count))
    successes = rng.binomial(repeats, graph_probabilities).sum(axis=2)
    return successes / (graph_count * repeats)


def simulate_job(
    *,
    stage: str,
    scenario: dict[str, float | str],
    scenario_index: int,
    graph_count: int,
    repeats: int,
    simulations: int,
    class_counts: Counter[str],
    exact: bool,
) -> list[dict[str, object]]:
    stage_code = 1 if exact else 0
    seed_sequence = seed_for(stage_code, scenario_index, graph_count, repeats)
    rng = np.random.default_rng(seed_sequence)
    estimate = exact_estimates if exact else normal_estimates
    agreement_by_class: dict[str, np.ndarray] = {}

    for label in ("visible", "partial", "blind"):
        count = class_counts[label]
        power_hat = estimate(
            rng,
            float(scenario[f"{label}_mean"]),
            graph_count,
            repeats,
            (simulations, count),
        )
        false_alarm_hat = estimate(
            rng,
            float(scenario["false_alarm_mean"]),
            graph_count,
            repeats,
            (simulations, count),
        )
        observed_visible = (power_hat >= VISIBLE_THRESHOLD) & (
            false_alarm_hat <= FALSE_ALARM_CEILING
        )
        observed_blind = (~observed_visible) & (power_hat <= BLIND_CEILING)
        observed_partial = (~observed_visible) & (~observed_blind)
        if label == "visible":
            agreement_by_class[label] = observed_visible.sum(axis=1)
        elif label == "blind":
            agreement_by_class[label] = observed_blind.sum(axis=1)
        else:
            agreement_by_class[label] = observed_partial.sum(axis=1)

    total_cells = sum(class_counts.values())
    minimum_agreements = minimum_agreements_for_success(total_cells)
    total_agreements = sum(agreement_by_class.values())
    rows: list[dict[str, object]] = []
    seed_key = f"{ROOT_SEED}:{stage_code}:{scenario_index}:{graph_count}:{repeats}"
    for simulation_index in range(simulations):
        agreements = int(total_agreements[simulation_index])
        lower, upper = wilson_interval(agreements, total_cells)
        rows.append(
            {
                "stage": stage,
                "model": "beta_binomial_exact" if exact else "normal_beta_binomial_mean",
                "scenario": scenario["name"],
                "graph_count": graph_count,
                "target_circuit_count": 2 * graph_count,
                "repeats_per_graph": repeats,
                "simulation_index": simulation_index,
                "seed_key": seed_key,
                "visible_agreements": int(
                    agreement_by_class["visible"][simulation_index]
                ),
                "partial_agreements": int(
                    agreement_by_class["partial"][simulation_index]
                ),
                "blind_agreements": int(
                    agreement_by_class["blind"][simulation_index]
                ),
                "total_agreements": agreements,
                "total_evaluable_cells": total_cells,
                "agreement_rate": agreements / total_cells,
                "wilson_lower": lower,
                "wilson_upper": upper,
                "minimum_agreements_for_success": minimum_agreements,
                "primary_success": int(agreements >= minimum_agreements),
            }
        )
    return rows


def summarize_job(
    rows: list[dict[str, object]], scenario: dict[str, float | str]
) -> dict[str, object]:
    successes = sum(int(row["primary_success"]) for row in rows)
    simulations = len(rows)
    power = successes / simulations
    lower, upper = wilson_interval(successes, simulations)
    target = float(scenario["target"])
    first = rows[0]
    return {
        "stage": first["stage"],
        "model": first["model"],
        "scenario": first["scenario"],
        "graph_count": first["graph_count"],
        "target_circuit_count": first["target_circuit_count"],
        "repeats_per_graph": first["repeats_per_graph"],
        "simulations": simulations,
        "estimated_power": power,
        "power_wilson_lower": lower,
        "power_wilson_upper": upper,
        "power_target": target,
        "point_margin_from_target": power - target,
        "lower_bound_margin_from_target": lower - target,
        "passes_point_target": int(power >= target),
        "passes_lower_target": int(lower >= target),
    }


def qualifying_designs(
    summary_rows: list[dict[str, object]], selection_basis: str
) -> list[tuple[int, int]]:
    pass_field = (
        "passes_lower_target" if selection_basis == "lower" else "passes_point_target"
    )
    by_design: dict[tuple[int, int], list[dict[str, object]]] = {}
    for row in summary_rows:
        key = (int(row["graph_count"]), int(row["repeats_per_graph"]))
        by_design.setdefault(key, []).append(row)
    qualifying = []
    for design, rows in by_design.items():
        if len(rows) == len(SCENARIOS) and all(
            int(row[pass_field]) == 1 for row in rows
        ):
            qualifying.append(design)
    return sorted(qualifying, key=lambda item: (2 * item[0] * item[1], item[0], item[1]))


def write_csv_exclusive(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write to {path}")
    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    if not args.matrix_committed_confirmed:
        raise SystemExit(
            "Refusing to run: pass --matrix-committed-confirmed only after the user "
            "confirms docs/theory/06_matrix.csv is committed."
        )

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.run_label}" if args.run_label else ""
    raw_path = output_dir / f"power_analysis_raw{suffix}.csv"
    summary_path = output_dir / f"power_analysis_summary{suffix}.csv"
    log_path = output_dir / f"run_log{suffix}.txt"
    for path in (raw_path, summary_path, log_path):
        if path.exists():
            raise SystemExit(f"Refusing to overwrite existing output: {path}")

    start = time.time()
    class_counts, unresolved, matrix_hash = load_matrix(args.matrix)
    if sum(class_counts.values()) == 0:
        raise SystemExit("No evaluable primary cells found")

    raw_rows: list[dict[str, object]] = []
    screen_summaries: list[dict[str, object]] = []
    for scenario_index, scenario in enumerate(SCENARIOS):
        for graph_count in GRAPH_COUNTS:
            for repeats in REPEAT_COUNTS:
                rows = simulate_job(
                    stage="screen",
                    scenario=scenario,
                    scenario_index=scenario_index,
                    graph_count=graph_count,
                    repeats=repeats,
                    simulations=SCREEN_SIMULATIONS,
                    class_counts=class_counts,
                    exact=False,
                )
                raw_rows.extend(rows)
                screen_summaries.append(summarize_job(rows, scenario))

    candidates = qualifying_designs(screen_summaries, args.selection_basis)
    if not candidates:
        raise SystemExit("No screened design met all prespecified power targets")

    exact_summaries: list[dict[str, object]] = []
    selected: tuple[int, int] | None = None
    for graph_count, repeats in candidates:
        candidate_summaries: list[dict[str, object]] = []
        for scenario_index, scenario in enumerate(SCENARIOS):
            rows = simulate_job(
                stage="exact_confirmation",
                scenario=scenario,
                scenario_index=scenario_index,
                graph_count=graph_count,
                repeats=repeats,
                simulations=EXACT_SIMULATIONS,
                class_counts=class_counts,
                exact=True,
            )
            raw_rows.extend(rows)
            candidate_summaries.append(summarize_job(rows, scenario))
        exact_summaries.extend(candidate_summaries)
        pass_field = (
            "passes_lower_target"
            if args.selection_basis == "lower"
            else "passes_point_target"
        )
        if all(int(row[pass_field]) == 1 for row in candidate_summaries):
            selected = (graph_count, repeats)
            break

    if selected is None:
        raise SystemExit("No exact-confirmed design met all prespecified power targets")

    summary_rows = screen_summaries + exact_summaries
    write_csv_exclusive(raw_path, raw_rows)
    write_csv_exclusive(summary_path, summary_rows)

    config_buffer = io.StringIO()
    with contextlib.redirect_stdout(config_buffer):
        np.show_config()

    selected_graphs, selected_repeats = selected
    family_base, family_remainder = divmod(selected_graphs, len(GRAPH_FAMILIES))
    family_counts = {
        name: family_base + int(index < family_remainder)
        for index, name in enumerate(GRAPH_FAMILIES)
    }
    strata = len(WIDTHS) * len(DEPTHS)
    if selected_graphs % strata != 0:
        raise RuntimeError("Selected graph count does not divide evenly across width-depth strata")
    graphs_per_stratum = selected_graphs // strata

    elapsed = time.time() - start
    with log_path.open("x", encoding="utf-8") as handle:
        handle.write("Power analysis run log\n")
        handle.write(f"command={' '.join(sys.argv)}\n")
        handle.write(f"run_label={args.run_label or 'unlabelled'}\n")
        handle.write(f"selection_basis={args.selection_basis}\n")
        handle.write("matrix_commit_confirmation=user supplied; Git history not inspected\n")
        handle.write(f"matrix_path={args.matrix}\n")
        handle.write(f"matrix_sha256={matrix_hash}\n")
        handle.write(f"root_seed={ROOT_SEED}\n")
        handle.write(
            "seed_derivation=SeedSequence([ROOT_SEED, stage, scenario, graphs, repeats])\n"
        )
        handle.write(f"python={sys.version}\n")
        handle.write(f"platform={platform.platform()}\n")
        handle.write(f"numpy={np.__version__}\n")
        handle.write(f"class_counts={dict(class_counts)}\n")
        handle.write(f"unresolved_primary_rows={unresolved}\n")
        handle.write(f"screen_simulations_per_job={SCREEN_SIMULATIONS}\n")
        handle.write(f"exact_simulations_per_job={EXACT_SIMULATIONS}\n")
        handle.write(f"graph_counts={GRAPH_COUNTS}\n")
        handle.write(f"repeat_counts={REPEAT_COUNTS}\n")
        handle.write(f"intraclass_correlation={INTRACLASS_CORRELATION}\n")
        handle.write(f"scenarios={SCENARIOS}\n")
        handle.write(f"selected_graphs={selected_graphs}\n")
        handle.write(f"selected_target_circuits={2 * selected_graphs}\n")
        handle.write(f"selected_repeats_per_graph={selected_repeats}\n")
        handle.write(f"widths={WIDTHS}\n")
        handle.write(f"depths={DEPTHS}\n")
        handle.write(f"graphs_per_width_depth_stratum={graphs_per_stratum}\n")
        handle.write(f"graph_family_counts={family_counts}\n")
        handle.write(
            "scope=all evaluable primary cells retained; P1b and GVS remain exploratory; "
            "unresolved labels are retained but not scored\n"
        )
        handle.write(f"elapsed_seconds={elapsed:.6f}\n")
        handle.write("\nnp.show_config()\n")
        handle.write(config_buffer.getvalue())

    print(f"Selected design: {selected_graphs} graphs, {2 * selected_graphs} target circuits")
    print(f"Repeats per graph: {selected_repeats}")
    print(f"Raw rows: {len(raw_rows)}")
    print(f"Matrix SHA-256: {matrix_hash}")
    print("Exact confirmation:")
    for row in exact_summaries[-len(SCENARIOS) :]:
        print(
            f"  {row['scenario']}: power={row['estimated_power']:.4f}, "
            f"target={row['power_target']:.2f}, "
            f"margin={row['point_margin_from_target']:+.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
