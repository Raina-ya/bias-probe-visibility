"""Ideal and noisy population gaps for the strength map and scoring.

Kept separate from ``execution.py`` and ``probes.py`` so that no probe can
receive a target ideal value.  Development values feed only the Section 4.2
strength map; holdout values are used only for immutable scoring after every
observed decision is written (protocol v3, Section 4.2).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import channels
import execution
import simulate

IDEAL_TIE = 1e-12


@dataclass(frozen=True)
class ReferenceGap:
    graph_id: str
    structure: str
    setting: str
    ideal_gap: float
    noisy_population_gap: float
    ideal_tie: bool

    @property
    def harmful_ratio(self) -> float:
        """Signed beta/Delta = (g_noisy - g) * sign(g) / |g|; NaN on an ideal tie."""

        if self.ideal_tie:
            return float("nan")
        return (
            (self.noisy_population_gap - self.ideal_gap)
            * np.sign(self.ideal_gap)
            / abs(self.ideal_gap)
        )

    @property
    def flipped(self) -> bool:
        """Section 11.4 flip-subset membership."""

        if self.ideal_tie:
            return False
        return self.noisy_population_gap == 0.0 or np.sign(
            self.noisy_population_gap
        ) != np.sign(self.ideal_gap)


def _population_gap(split, record, condition, cache, readout_time=None) -> float:
    scores = simulate.cut_scores(record.width, record.edges)
    targets = execution.target_circuits(split, record, condition)
    values = []
    for circuit in targets:
        pre = cache.get(circuit, condition.gate)
        if condition.readout_kind == "e6":
            # Population average over the eight target blocks the probe schedules use is
            # schedule-dependent; the time-averaged rates are used here (Section 4.1:
            # the E6 ratio does not depend on delta).
            readout = channels.readout_for(
                condition,
                record.width,
                record.first_edge,
                record.first_connected_triple,
                0.5,
            )
        else:
            readout = channels.readout_for(
                condition,
                record.width,
                record.first_edge,
                record.first_connected_triple,
            )
        values.append(
            channels.apply_readout(pre, record.width, readout) @ scores
            + condition.offset
        )
    return float(values[0] - values[1])


def reference_gap(
    split: str, record, structure: str, setting: str, cache=None
) -> ReferenceGap:
    cache = cache if cache is not None else execution.SolveCache()
    clean = channels.parse_condition("E0", "0.0")
    ideal = _population_gap(split, record, clean, cache)
    noisy = _population_gap(
        split, record, channels.parse_condition(structure, setting), cache
    )
    return ReferenceGap(
        record.graph_id, structure, setting, ideal, noisy, abs(ideal) <= IDEAL_TIE
    )
