"""Pre-data audit of the five v3 P4 cells (analytic, exact; split 99 widths).

Under E0 there is no readout error, so every P4a/P4b preparation returns its
prepared string with probability 1 and both statistics are identically 0; the
Section 6.1 threshold is therefore tau = 0 and the alarm is T > 0.  Under a
structure the statistic is 0 only if no preparation shot shows any flip, so
P(no alarm) <= P(no flip in every probe shot) is computed exactly here at the
v3 main fraction (n_P = 1,638 shots split over the probe circuits).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

N_P = 1638


def log_no_flip_p4a(width, rates):
    """Prep0 and prep1 each receive N_P/2 shots; rates[q] = (Pr(1|0), Pr(0|1))."""

    shots = N_P // 2
    lp0 = sum(math.log1p(-a) for a, _ in rates)
    lp1 = sum(math.log1p(-b) for _, b in rates)
    return shots * (lp0 + lp1)


def log_no_flip_p4b_pairflips(width, marginal_on, marginal):
    """A preparation shows a flip unless every flipping qubit is unflipped."""

    circuits = 4 * math.comb(width, 2)
    shots = N_P // circuits
    return circuits * shots * len(marginal_on) * math.log1p(-marginal)


def main() -> int:
    print("width cell log10_P(no_alarm)_upper_bound")
    for width in (4, 8):
        cells = {
            "P4a/E5 (pair flips 0.10)": log_no_flip_p4a(
                width, [(0.10, 0.10)] * 2 + [(0, 0)] * (width - 2)
            ),
            "P4a/E5' (triple flips 0.25)": log_no_flip_p4a(
                width, [(0.25, 0.25)] * 3 + [(0, 0)] * (width - 3)
            ),
            "P4b/E5' (triple flips 0.25)": log_no_flip_p4b_pairflips(
                width, (0, 1, 2), 0.25
            ),
            "P4a/E6 (rates >= 0.04/0.03)": log_no_flip_p4a(
                width, [(0.04, 0.03)] * width
            ),
            "P4b/E6 (rates >= 0.04/0.03)": log_no_flip_p4b_pairflips(
                width, tuple(range(width)), 0.03
            ),
        }
        for name, value in cells.items():
            print(f"{width} {name} {value / math.log(10):.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
