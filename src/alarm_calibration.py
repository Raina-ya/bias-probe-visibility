"""E0 alarm calibration, protocol v2 Section 6.1.

Within each width-depth stratum, sort the n development E0 scores and set
``tau = T_(min(n, ceil((n+1)*(1-alpha))))`` (1-indexed order statistic).  The
alarm is strict, ``T > tau``.  The rank uses exact rational arithmetic so that
floating-point rounding of ``(n+1)*(1-alpha)`` cannot move the threshold.
"""

from __future__ import annotations

import math
from collections import defaultdict
from fractions import Fraction
from typing import Iterable, Mapping, Sequence


MAIN_ALPHA = "0.05"
SENSITIVITY_ALPHAS = ("0.01", "0.10")


def order_rank(n: int, alpha: str) -> int:
    if n <= 0:
        raise ValueError("at least one E0 score is required")
    level = Fraction(alpha)
    if not 0 < level < 1:
        raise ValueError("alpha must lie in (0,1)")
    return min(n, math.ceil((n + 1) * (1 - level)))


def threshold(scores: Sequence[float], alpha: str = MAIN_ALPHA) -> float:
    if any(score < 0 or math.isnan(score) for score in scores):
        raise ValueError("composite alarm scores must be nonnegative numbers")
    ordered = sorted(scores)
    return ordered[order_rank(len(ordered), alpha) - 1]


def calibrate(
    rows: Iterable[tuple[tuple[int, int], float]], alpha: str = MAIN_ALPHA
) -> dict[tuple[int, int], float]:
    """Map ``(width, depth)`` to its E0 threshold."""

    grouped: dict[tuple[int, int], list[float]] = defaultdict(list)
    for stratum, score in rows:
        grouped[stratum].append(score)
    return {
        stratum: threshold(scores, alpha) for stratum, scores in sorted(grouped.items())
    }


def alarm(
    score: float, stratum: tuple[int, int], thresholds: Mapping[tuple[int, int], float]
) -> bool:
    return score > thresholds[stratum]
