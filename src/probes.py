"""Frozen probe statistics, protocol v3 Section 6.2.

Every function here receives only observed counts and, for P2, the twin
circuit's own noiseless reference gap.  No function accepts a target ideal
value; ``tests/test_execution.py`` enforces this by inspecting signatures.
Counts are dictionaries mapping bit strings ``z_0...z_{w-1}`` to integers.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import protocol_contract as contract

Counts = Mapping[str, int]


def _total(counts: Counts) -> int:
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("empty counts")
    return total


def mean_score(counts: Counts, edges: Sequence[tuple[int, int]]) -> float:
    total = _total(counts)
    value = 0.0
    for z, n in counts.items():
        value += n * sum(z[i] != z[j] for i, j in edges) / len(edges)
    return value / total


def gap(counts_a: Counts, counts_b: Counts, edges, offset: float = 0.0) -> float:
    """Sample gap mu_A - mu_B; E0 adds the same offset to both values."""

    return (mean_score(counts_a, edges) + offset) - (
        mean_score(counts_b, edges) + offset
    )


def distribution(counts: Counts) -> dict[str, float]:
    total = _total(counts)
    return {z: n / total for z, n in counts.items()}


# ---------------------------------------------------------------- statistics


def p0_lower_bound(
    counts_a: Counts, counts_b: Counts, edges, offset: float = 0.0
) -> float:
    return contract.hoeffding_selected_lcb(
        gap(counts_a, counts_b, edges, offset),
        _total(counts_a),
        _total(counts_b),
        0.025,
    )


def p1_score(targets: Sequence[Counts], folded: Sequence[Counts], edges) -> float:
    g1 = gap(targets[0], targets[1], edges)
    g3 = gap(folded[0], folded[1], edges)
    return abs((g3 - g1) / 2.0)


def p2_score(twins: Sequence[Counts], edges, twin_reference_gap: float) -> float:
    """``twin_reference_gap`` is the twin circuits' own noiseless gap."""

    return abs(gap(twins[0], twins[1], edges) - twin_reference_gap)


def p3_score(
    targets: Sequence[Counts],
    frames_a: Sequence[Counts],
    frames_b: Sequence[Counts],
    edges,
) -> float:
    if len(frames_a) != 16 or len(frames_b) != 16:
        raise ValueError("P3 needs 16 framed versions per candidate")
    plain = gap(targets[0], targets[1], edges)
    framed = sum(gap(a, b, edges) for a, b in zip(frames_a, frames_b, strict=True)) / 16
    return abs(plain - framed)


def _one_rate(counts: Counts, qubit: int) -> float:
    total = _total(counts)
    return sum(n for z, n in counts.items() if z[qubit] == "1") / total


def p4a_score(prep0: Counts, prep1: Counts, width: int) -> float:
    return max(
        max(abs(_one_rate(prep0, q) - 0.0), abs(_one_rate(prep1, q) - 1.0))
        for q in range(width)
    )


def _pair_counts(counts: Counts, i: int, j: int) -> dict[str, int]:
    out = {"00": 0, "01": 0, "10": 0, "11": 0}
    for z, n in counts.items():
        out[z[i] + z[j]] += n
    return out


def p4b_score(
    pair_preps: Mapping[tuple[int, int], Mapping[tuple[int, int], Counts]],
) -> float:
    """``pair_preps[(i,j)][(a,b)]`` holds full counts of the pair-preparation circuit."""

    scores = []
    for (i, j), preps in pair_preps.items():
        observations = {prep: _pair_counts(c, i, j) for prep, c in preps.items()}
        scores.append(contract.p4b_score(observations))
    return max(scores)


def complement_score(counts: Counts) -> float:
    p = distribution(counts)
    width = len(next(iter(p)))
    full = {
        format(k, f"0{width}b"): p.get(format(k, f"0{width}b"), 0.0)
        for k in range(2**width)
    }
    return (
        contract.complement_asymmetry(full)
        if math.isclose(sum(full.values()), 1.0)
        else math.nan
    )


def p5_score(
    targets: Sequence[Counts], halves: Sequence[Sequence[Counts]] | None = None
) -> float:
    """Max complement asymmetry over candidates; E6 adds half-scores and their difference."""

    values = [complement_score(c) for c in targets]
    if halves is not None:
        for first, second in halves:
            s1, s2 = complement_score(first), complement_score(second)
            values += [s1, s2, abs(s1 - s2)]
    return max(values)


def p1b_score(targets: Sequence[Counts], folded: Sequence[Counts]) -> float:
    """W_neg of the scale-1/3 Richardson distribution, max over candidates."""

    worst = 0.0
    for scale1, scale3 in zip(targets, folded, strict=True):
        p1, p3 = distribution(scale1), distribution(scale3)
        w = 0.0
        for z in set(p1) | set(p3):
            value = 1.5 * p1.get(z, 0.0) - 0.5 * p3.get(z, 0.0)
            if value < 0:
                w += -value
        worst = max(worst, w)
    return worst


def gvs_score(*_args, **_kwargs) -> float:
    """GVS (exploratory) is not implemented: L_C and K must be fixed from the source first."""

    raise NotImplementedError("GVS needs the owner's frozen L_C and K definitions")
