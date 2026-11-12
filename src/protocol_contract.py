"""Executable, outcome-free contract for protocol v2.

This module performs deterministic allocation, hash, statistic, and resource
checks.  It does not construct noisy circuits or draw shot outcomes.
"""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from hashing import canonical_sha256  # noqa: E402


ROOT_SEED = 20261111
TOTAL_SHOTS = 16_384
REPEATS = 32
PRIMARY_PROBES = ("P0", "P1", "P2", "P3", "P4a", "P4b", "P5")
PRIMARY_STRUCTURES = ("E0", "E1", "E2", "E3", "E4", "E5", "E5'", "E6")
PARAMETER_COUNTS = {
    "E0": 7,
    "E1": 5,
    "E2": 8,
    "E3": 8,
    "E4": 8,
    "E5": 8,
    "E5'": 8,
    "E6": 8,
}
WIDTHS = (4, 5, 6, 7, 8)
DEPTHS = (1, 2, 3, 4, 5)
GRAPHS_PER_WIDTH_DEPTH = 6  # two development plus four holdout
MATRIX_SHA256 = "7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995"
EXPECTED_PRIMARY_COUNTS = Counter({"blind": 35, "partial": 15, "visible": 6})
MAX_PROBABILITY_SOLVES = 2_000_000
MAX_AGGREGATE_ROWS = 5_000_000
MAX_RAW_BYTES = 20 * 1024**3

SPLIT_CODES = {
    "development": 10,
    "holdout": 20,
    "prop1_pilot": 30,
    "prop1_scoring": 31,
    "e7_exploratory": 40,
    "software_test": 99,
}


@dataclass(frozen=True)
class ResourceEstimate:
    graphs: int
    parameter_conditions: int
    aggregate_rows: int
    nominal_shots: int
    unique_probability_solves: int
    projected_raw_bytes: int

    @property
    def within_structural_caps(self) -> bool:
        return (
            self.aggregate_rows <= MAX_AGGREGATE_ROWS
            and self.unique_probability_solves <= MAX_PROBABILITY_SOLVES
            and self.projected_raw_bytes <= MAX_RAW_BYTES
        )

    def to_dict(self) -> dict[str, int | bool]:
        result = asdict(self)
        result["within_structural_caps"] = self.within_structural_caps
        return result


def sha256_file(path: Path) -> str:
    return canonical_sha256(path)


def validate_matrix(path: Path) -> Counter[str]:
    actual_hash = sha256_file(path)
    if actual_hash != MATRIX_SHA256:
        raise ValueError(f"matrix hash mismatch: {actual_hash}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    primary = [row for row in rows if row["probe"] in PRIMARY_PROBES]
    counts = Counter(row["prediction"] for row in primary)
    if len(primary) != 56 or counts != EXPECTED_PRIMARY_COUNTS:
        raise ValueError(f"matrix contract mismatch: cells={len(primary)}, counts={counts}")
    return counts


def split_even(total: int, labels: Sequence[str]) -> dict[str, int]:
    if total < 0 or not labels:
        raise ValueError("total must be nonnegative and labels must be nonempty")
    quotient, remainder = divmod(total, len(labels))
    allocation = {
        label: quotient + (index < remainder) for index, label in enumerate(labels)
    }
    if sum(allocation.values()) != total:
        raise AssertionError("allocation does not conserve shots")
    return allocation


def seed_key(
    *,
    split: str,
    artifact_code: int,
    structure_code: int,
    probe_code: int,
    width: int,
    depth: int,
    graph_index: int,
    candidate_index: int,
    repeat_index: int,
    parameter_index: int,
    allow_holdout: bool = False,
) -> tuple[int, ...]:
    split_code = SPLIT_CODES[split]
    if split_code in {20, 31} and not allow_holdout:
        raise PermissionError("confirmatory seed namespace is locked")
    return (
        ROOT_SEED,
        split_code,
        artifact_code,
        structure_code,
        probe_code,
        width,
        depth,
        graph_index,
        candidate_index,
        repeat_index,
        parameter_index,
    )


def hoeffding_selected_lcb(
    observed_gap: float,
    n_a: int,
    n_b: int,
    alpha_t: float = 0.025,
) -> float:
    if n_a <= 0 or n_b <= 0 or not 0 < alpha_t < 1:
        raise ValueError("positive shot counts and alpha_t in (0,1) are required")
    h_a = math.sqrt(math.log(4.0 / alpha_t) / (2.0 * n_a))
    h_b = math.sqrt(math.log(4.0 / alpha_t) / (2.0 * n_b))
    return abs(observed_gap) - h_a - h_b


def complement_asymmetry(probabilities: Mapping[str, float]) -> float:
    if not probabilities:
        raise ValueError("probabilities must be nonempty")
    width = len(next(iter(probabilities)))
    if any(len(bitstring) != width for bitstring in probabilities):
        raise ValueError("bitstrings must have one width")
    total = sum(probabilities.values())
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError(f"probabilities sum to {total}")
    distance = 0.0
    for bitstring, probability in probabilities.items():
        complement = "".join("1" if bit == "0" else "0" for bit in bitstring)
        distance += abs(probability - probabilities.get(complement, 0.0))
    return 0.5 * distance


def p4b_components(
    observations: Mapping[tuple[int, int], Mapping[str, int]],
) -> tuple[float, float]:
    """Return marginal-assignment and pair-correlation maxima.

    Keys are prepared pair bits, for example ``(0, 1)``.  Count dictionaries
    use output strings ``00``, ``01``, ``10``, and ``11``.
    """

    required = {(0, 0), (0, 1), (1, 0), (1, 1)}
    if set(observations) != required:
        raise ValueError("all four pair preparations are required")
    marginal_max = 0.0
    correlation_max = 0.0
    outcomes = ("00", "01", "10", "11")
    for prepared, counts in observations.items():
        total = sum(counts.get(outcome, 0) for outcome in outcomes)
        if total <= 0:
            raise ValueError("every preparation needs positive counts")
        probabilities = {outcome: counts.get(outcome, 0) / total for outcome in outcomes}
        p_i1 = probabilities["10"] + probabilities["11"]
        p_j1 = probabilities["01"] + probabilities["11"]
        marginal_max = max(
            marginal_max,
            abs(p_i1 - prepared[0]),
            abs(p_j1 - prepared[1]),
        )
        product = {
            "00": (1 - p_i1) * (1 - p_j1),
            "01": (1 - p_i1) * p_j1,
            "10": p_i1 * (1 - p_j1),
            "11": p_i1 * p_j1,
        }
        tv = 0.5 * sum(abs(probabilities[key] - product[key]) for key in outcomes)
        correlation_max = max(correlation_max, tv)
    return marginal_max, correlation_max


def p4b_score(observations: Mapping[tuple[int, int], Mapping[str, int]]) -> float:
    return max(p4b_components(observations))


def choose_strength(
    candidates: Iterable[tuple[float, float]], target_ratio: float
) -> tuple[float, float]:
    """Choose ``(strength, development_median_ratio)`` deterministically."""

    rows = list(candidates)
    if not rows:
        raise ValueError("at least one strength is required")
    return min(
        rows,
        key=lambda row: (
            abs(row[1] - target_ratio),
            abs(row[0]),
            row[0],
        ),
    )


def _circuit_solves(probe: str, width: int, temporal: bool) -> int:
    pairs = math.comb(width, 2)
    if not temporal:
        return {
            "P0": 2,
            "P1": 4,
            "P2": 4,
            "P3": 34,
            "P4a": 4,
            "P4b": 2 + 4 * pairs,
            "P5": 2,
        }[probe]
    return {
        "P0": 16,
        "P1": 8,
        "P2": 8,
        "P3": 68,
        "P4a": 16,
        "P4b": 12 + 8 * pairs,
        "P5": 16,
    }[probe]


def _outcome_slots(probe: str, width: int, temporal: bool) -> int:
    full = 2**width
    pairs = math.comb(width, 2)
    if probe == "P4b":
        return (12 if temporal else 2) * full + (8 if temporal else 4) * pairs * 4
    return _circuit_solves(probe, width, temporal) * full


def estimate_resources() -> ResourceEstimate:
    graphs_per_width = GRAPHS_PER_WIDTH_DEPTH * len(DEPTHS)
    graph_count = graphs_per_width * len(WIDTHS)
    parameter_conditions = sum(PARAMETER_COUNTS.values())
    aggregate_rows = (
        graph_count
        * len(PRIMARY_PROBES)
        * parameter_conditions
        * REPEATS
    )
    nominal_shots = aggregate_rows * TOTAL_SHOTS

    normal_conditions = parameter_conditions - PARAMETER_COUNTS["E6"]
    drift_conditions = PARAMETER_COUNTS["E6"]
    unique_solves = 0
    projected_bytes = 0
    row_metadata_bytes = 512
    count_bytes = 8
    for width in WIDTHS:
        for probe in PRIMARY_PROBES:
            unique_solves += graphs_per_width * (
                normal_conditions * _circuit_solves(probe, width, False)
                + drift_conditions * _circuit_solves(probe, width, True)
            )
            normal_row_bytes = row_metadata_bytes + count_bytes * _outcome_slots(
                probe, width, False
            )
            drift_row_bytes = row_metadata_bytes + count_bytes * _outcome_slots(
                probe, width, True
            )
            projected_bytes += graphs_per_width * REPEATS * (
                normal_conditions * normal_row_bytes
                + drift_conditions * drift_row_bytes
            )

    return ResourceEstimate(
        graphs=graph_count,
        parameter_conditions=parameter_conditions,
        aggregate_rows=aggregate_rows,
        nominal_shots=nominal_shots,
        unique_probability_solves=unique_solves,
        projected_raw_bytes=projected_bytes,
    )


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    counts = validate_matrix(repo / "docs" / "theory" / "06_matrix.csv")
    estimate = estimate_resources()
    print(f"matrix_counts={dict(sorted(counts.items()))}")
    for key, value in estimate.to_dict().items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
