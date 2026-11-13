"""Protocol v4 analysis: decision endpoints (Section 11.1-11.2) and stratified
visibility agreement (Section 11.3).

Inputs are arrays written from raw rows and, for scoring, the ideal winner of
each graph from ``reference.py`` (used only after every decision is written).
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

import analysis

NO_PROBLEM_BOUND = 0.01
BOOTSTRAP = 10_000


def false_certification(
    certified: np.ndarray, winner: np.ndarray, ideal_winner: np.ndarray
) -> np.ndarray:
    """``winner`` and ``ideal_winner`` are +1 (A), -1 (B), or 0 (tie).

    Arrays are graphs x repeats; ``ideal_winner`` is per graph.  A certified
    ideal tie counts as false (v3 Section 2.3 retained).
    """

    ideal = ideal_winner[:, None]
    wrong = (winner != ideal) | (ideal == 0)
    return certified & wrong


@dataclass(frozen=True)
class DecisionResult:
    dfc: float
    dfc_lower: float
    dfc_upper: float
    fc0: float
    fc0_upper: float
    coverage_loss: float
    outcome: str


def _strata_indices(strata: Sequence[tuple[int, int]], rng, size: int) -> np.ndarray:
    return np.stack([analysis.stratified_indices(strata, rng) for _ in range(size)])


def primary_decision(
    fc_r0: Mapping[str, np.ndarray],
    fc_r1: Mapping[str, np.ndarray],
    cov_r0: Mapping[str, np.ndarray],
    cov_r1: Mapping[str, np.ndarray],
    strata: Sequence[tuple[int, int]],
    rng: np.random.Generator,
    resamples: int = BOOTSTRAP,
    no_problem_bound: float = NO_PROBLEM_BOUND,
) -> DecisionResult:
    """Pooled dFC over structures with equal weights; arrays are graphs x repeats of 0/1."""

    structures = sorted(fc_r0)
    a0 = np.stack([fc_r0[s].astype(float) for s in structures])  # S x G x R
    a1 = np.stack([fc_r1[s].astype(float) for s in structures])
    c0 = np.stack([cov_r0[s].astype(float) for s in structures])
    c1 = np.stack([cov_r1[s].astype(float) for s in structures])
    point = float((a0 - a1).mean())
    dfc_b = np.empty(resamples)
    fc0_b = np.empty(resamples)
    for b in range(resamples):
        idx = analysis.stratified_indices(strata, rng)  # shared by structures and rules
        dfc_b[b] = (a0[:, idx] - a1[:, idx]).mean()
        fc0_b[b] = a0[:, idx].mean()
    lo, hi = np.percentile(dfc_b, [2.5, 97.5], method="inverted_cdf")
    fc0_hi = float(np.percentile(fc0_b, 97.5, method="inverted_cdf"))
    if lo > 0:
        outcome = "improvement"
    elif fc0_hi < no_problem_bound:
        outcome = "no_problem"
    else:
        outcome = "inconclusive"
    return DecisionResult(
        dfc=point,
        dfc_lower=float(lo),
        dfc_upper=float(hi),
        fc0=float(a0.mean()),
        fc0_upper=fc0_hi,
        coverage_loss=float(c0.mean() - c1.mean()),
        outcome=outcome,
    )


def interception(
    fc_r0: np.ndarray, certified_r1: np.ndarray, minimum: int = 5
) -> tuple[float, int]:
    """Fraction of R0 false certifications where R1 does not certify (paired units)."""

    units = int(fc_r0.sum())
    if units < minimum:
        return math.nan, units
    return float((~certified_r1[fc_r0.astype(bool)]).mean()), units


def stratified_agreement(
    predicted: Mapping[tuple[str, str], str],
    strata_of: Mapping[tuple[str, str], str],
    alarms: Mapping[tuple[str, str], np.ndarray],
    null_alarms: Mapping[tuple[str, str], np.ndarray],
    graph_strata: Sequence[tuple[int, int]],
    rng: np.random.Generator,
    resamples: int = BOOTSTRAP,
) -> dict[str, tuple[float, float, float, int]]:
    """Agreement per stratum: (point, lower, upper, cells).  Never pooled."""

    def labels(index):
        out = {}
        for cell, a in alarms.items():
            n = null_alarms[cell]
            if index is not None:
                a, n = a[index], n[index]
            power = float(np.mean(a)) if not np.isnan(a).any() else math.nan
            fa = float(np.mean(n)) if not np.isnan(n).any() else math.nan
            out[cell] = analysis.classify(power, fa)
        return out

    result = {}
    for stratum in sorted(set(strata_of.values())):
        cells = [c for c in predicted if strata_of[c] == stratum]

        def agree(lab, cells=cells):
            return sum(
                lab.get(c, analysis.NOT_EVALUABLE) == predicted[c] for c in cells
            ) / len(cells)

        point = agree(labels(None))
        boot = np.array(
            [
                agree(labels(analysis.stratified_indices(graph_strata, rng)))
                for _ in range(resamples)
            ]
        )
        lo, hi = np.percentile(boot, [2.5, 97.5], method="inverted_cdf")
        result[stratum] = (point, float(lo), float(hi), len(cells))
    return result
