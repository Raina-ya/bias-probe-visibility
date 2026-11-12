"""Outcome-free analysis skeleton for protocol v2, Sections 8 and 11.

Inputs are alarm indicators already produced by the frozen probes and, for the
certificate, probe event counts.  No function here reads a target ideal value.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np


POWER_VISIBLE = 0.80
FALSE_ALARM_VISIBLE = 0.10
POWER_BLIND = 0.10
PRIMARY_SUCCESS = 0.80
BOOTSTRAP_RESAMPLES = 10_000
LABELS = ("visible", "partial", "blind")
NOT_EVALUABLE = "not_evaluable"


@dataclass(frozen=True)
class Thresholds:
    power_visible: float = POWER_VISIBLE
    false_alarm_visible: float = FALSE_ALARM_VISIBLE
    power_blind: float = POWER_BLIND


DEFAULT_THRESHOLDS = Thresholds()


def classify(
    power: float, false_alarm: float, thresholds: Thresholds = DEFAULT_THRESHOLDS
) -> str:
    """Section 8 label.  NaN inputs are not evaluable (a disagreement)."""

    if math.isnan(power) or math.isnan(false_alarm):
        return NOT_EVALUABLE
    if (
        power >= thresholds.power_visible
        and false_alarm <= thresholds.false_alarm_visible
    ):
        return "visible"
    if power <= thresholds.power_blind:
        return "blind"
    return "partial"


def threshold_distance(value: float, threshold: float, upper_limit: bool) -> str:
    """Signed ``value-threshold``; for an upper limit a negative distance is favourable."""

    distance = value - threshold
    note = ""
    if upper_limit and distance < 0:
        note = " (favourable: below upper limit)"
    return f"{distance:+.4f}{note}"


def cell_rates(
    alarms: Mapping[tuple[str, str], np.ndarray],
    e0_alarms: Mapping[str, np.ndarray],
    graph_index: np.ndarray | None = None,
) -> dict[tuple[str, str], tuple[float, float]]:
    """Return ``(power, matching E0 false-alarm)`` per (probe, structure).

    ``alarms[(probe, structure)]`` has shape ``(graphs, repeats)``; missing or
    unattainable cells are passed as all-NaN arrays.  ``e0_alarms[probe]`` has
    shape ``(graphs, repeats * 7)`` with the seven common-mode values equally
    represented.  ``graph_index`` selects (possibly repeated) graph rows.
    """

    rates: dict[tuple[str, str], tuple[float, float]] = {}
    for (probe, structure), values in alarms.items():
        e0 = e0_alarms[probe]
        if graph_index is not None:
            values = values[graph_index]
            e0 = e0[graph_index]
        power = float(np.mean(values)) if not np.isnan(values).any() else math.nan
        false_alarm = float(np.mean(e0)) if not np.isnan(e0).any() else math.nan
        rates[(probe, structure)] = (power, false_alarm)
    return rates


def agreement(
    predicted: Mapping[tuple[str, str], str],
    observed: Mapping[tuple[str, str], str],
) -> float:
    cells = list(predicted)
    if len(cells) != 56:
        raise ValueError(f"primary endpoint needs 56 cells, got {len(cells)}")
    hits = sum(observed.get(cell, NOT_EVALUABLE) == predicted[cell] for cell in cells)
    return hits / len(cells)


def stratified_indices(
    strata: Sequence[tuple[int, int]], rng: np.random.Generator
) -> np.ndarray:
    """Resample graph indices with replacement within each width-depth stratum."""

    strata_array = np.array([f"{w}-{d}" for w, d in strata])
    picked: list[np.ndarray] = []
    for label in sorted(set(strata_array)):
        members = np.flatnonzero(strata_array == label)
        picked.append(rng.choice(members, size=members.size, replace=True))
    return np.concatenate(picked)


@dataclass(frozen=True)
class PrimaryResult:
    point: float
    lower: float
    upper: float
    success: bool
    distance_from_threshold: str


def primary_endpoint(
    predicted: Mapping[tuple[str, str], str],
    alarms: Mapping[tuple[str, str], np.ndarray],
    e0_alarms: Mapping[str, np.ndarray],
    strata: Sequence[tuple[int, int]],
    rng: np.random.Generator,
    resamples: int = BOOTSTRAP_RESAMPLES,
    thresholds: Thresholds = DEFAULT_THRESHOLDS,
) -> PrimaryResult:
    def labels(index: np.ndarray | None) -> dict[tuple[str, str], str]:
        rates = cell_rates(alarms, e0_alarms, index)
        return {cell: classify(*rates[cell], thresholds) for cell in rates}

    point = agreement(predicted, labels(None))
    values = np.empty(resamples)
    for b in range(resamples):
        index = stratified_indices(strata, rng)  # shared by every cell
        values[b] = agreement(predicted, labels(index))
    lower, upper = np.percentile(values, [2.5, 97.5], method="inverted_cdf")
    return PrimaryResult(
        point=point,
        lower=float(lower),
        upper=float(upper),
        success=bool(lower >= PRIMARY_SUCCESS),
        distance_from_threshold=threshold_distance(
            float(lower), PRIMARY_SUCCESS, False
        ),
    )


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    radius = (
        z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    )
    return centre - radius, centre + radius


# ---------------------------------------------------------------- certificate

CERTIFICATE_CELLS = frozenset({("P4a", "E4"), ("P4b", "E4"), ("P4b", "E5")})


def clopper_pearson(successes: int, total: int, alpha: float) -> tuple[float, float]:
    from scipy.stats import beta  # local import: only the certificate needs SciPy

    lower = (
        0.0
        if successes == 0
        else float(beta.ppf(alpha / 2, successes, total - successes + 1))
    )
    upper = (
        1.0
        if successes == total
        else float(beta.ppf(1 - alpha / 2, successes + 1, total - successes))
    )
    return lower, upper


def simultaneous_intervals(
    events: Sequence[tuple[int, int]], alpha_p: float = 0.025
) -> list[tuple[float, float]]:
    """Bonferroni-allocated Clopper-Pearson intervals for ``(count, shots)`` events."""

    per_event = alpha_p / len(events)
    return [clopper_pearson(count, shots, per_event) for count, shots in events]


def retained_channels(
    intervals: Sequence[tuple[float, float]],
    predicted: Mapping[str, Sequence[float]],
) -> list[str]:
    """Grid channels whose predicted event probabilities all lie inside the intervals."""

    kept = []
    for name, probabilities in predicted.items():
        if len(probabilities) != len(intervals):
            raise ValueError(f"channel {name}: wrong number of event probabilities")
        if all(
            lo <= p <= hi for p, (lo, hi) in zip(probabilities, intervals, strict=True)
        ):
            kept.append(name)
    return kept


def readout_bias_bound(score: np.ndarray, assignment: np.ndarray) -> float:
    """``b_G(e)=max_j v_j - min_j v_j`` with ``v = c^T (M_e - I)``."""

    size = score.size
    if assignment.shape != (size, size):
        raise ValueError("assignment matrix must be 2^w by 2^w")
    if not np.allclose(assignment.sum(axis=0), 1.0, atol=1e-12):
        raise ValueError("assignment matrix columns must sum to one")
    v = score @ (assignment - np.eye(size))
    return float(v.max() - v.min())


def certificate_bound(
    cell: tuple[str, str],
    score: np.ndarray,
    retained: Sequence[str],
    channels: Mapping[str, np.ndarray],
) -> float:
    """``B(D_P)``; +infinity outside the validated envelope or for an empty set."""

    if cell not in CERTIFICATE_CELLS or not retained:
        return math.inf
    try:
        return max(readout_bias_bound(score, channels[name]) for name in retained)
    except (KeyError, ValueError):
        return math.inf


def certify(lower_target_bound: float, bias_bound: float) -> bool:
    return lower_target_bound > bias_bound
