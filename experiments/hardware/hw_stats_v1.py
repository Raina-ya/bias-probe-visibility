"""Statistics for the hardware readout amendment v1 (shared by planning and analysis).

A pair-preparation table holds flip counts ``(n00, n01, n10, n11)``: index 0 is
"neither qubit flipped", 3 is "both flipped", and in ``n01``/``n10`` the first
digit is qubit i (the lower logical index), the second qubit j.  Definitions
follow docs/hardware/amendment_readout_v1.md, Sections 2 and 3.
"""

from __future__ import annotations

import math

import numpy as np

ALPHA = 0.05


def r_ind(qi: float, qj: float) -> float:
    """Parity-flip rate the independent (tensored) readout model assumes."""

    return qi + qj - 2.0 * qi * qj


def c_star(qi: float, qj: float) -> float:
    """Covariance above which independent-model mitigation of <ZiZj> is worse than raw.

    Observed parity flips at r = r_ind - 2c.  Raw error is 2r|<ZZ>|; the
    independent-model estimate errs by 4|c| / (1 - 2 r_ind) |<ZZ>|.  Equality for
    c > 0 gives c* = r_ind (1 - 2 r_ind) / (4 (1 - r_ind)).
    """

    r = r_ind(qi, qj)
    return r * (1.0 - 2.0 * r) / (4.0 * (1.0 - r))


def c_max(qi: float, qj: float) -> float:
    return min(qi, qj) - qi * qj


def joint(qi: float, qj: float, c: float) -> np.ndarray:
    """Probabilities of flip patterns (00, 01, 10, 11)."""

    p = np.array(
        [(1 - qi) * (1 - qj) + c, (1 - qi) * qj - c, qi * (1 - qj) - c, qi * qj + c]
    )
    if (p < -1e-15).any():
        raise ValueError("infeasible covariance")
    p = np.clip(p, 0.0, None)
    return p / p.sum()


def fisher_two_sided(n00: int, n01: int, n10: int, n11: int) -> float:
    """Two-sided Fisher exact p-value: sum of tables no more probable (Fisher 1935)."""

    row1, col1, n = n10 + n11, n01 + n11, n00 + n01 + n10 + n11
    lo, hi = max(0, row1 + col1 - n), min(row1, col1)
    if lo == hi:
        return 1.0
    k = np.arange(lo, hi + 1)
    lg = np.vectorize(math.lgamma)
    logp = (
        lg(row1 + 1) + lg(n - row1 + 1) + lg(col1 + 1) + lg(n - col1 + 1) - lg(n + 1)
        - lg(k + 1) - lg(row1 - k + 1) - lg(col1 - k + 1) - lg(n - row1 - col1 + k + 1)
    )
    obs = logp[n11 - lo]
    return float(min(1.0, np.exp(logp[logp <= obs + 1e-7]).sum()))


def estimates(counts: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Row-wise (q_i hat, q_j hat, c hat) from (n00, n01, n10, n11) counts."""

    n = counts.sum(axis=-1)
    p = counts / n[..., None]
    qi = p[..., 2] + p[..., 3]
    qj = p[..., 1] + p[..., 3]
    return qi, qj, p[..., 3] - qi * qj


def relevance_stat(counts: np.ndarray) -> np.ndarray:
    qi, qj, c = estimates(counts)
    return c - c_star(qi, qj)


def relevance_p(counts: np.ndarray, rng: np.random.Generator, boot: int) -> float:
    """One-sided parametric-bootstrap p-value for H0: c <= c*(q_i, q_j)."""

    n = int(counts.sum())
    qi, qj, _ = estimates(counts[None, :])
    qi, qj = float(qi[0]), float(qj[0])
    t_obs = float(relevance_stat(counts[None, :])[0])
    c0 = min(c_star(qi, qj), c_max(qi, qj))
    sims = rng.multinomial(n, joint(qi, qj, c0), size=boot)
    t = relevance_stat(sims)
    return (1 + int((t >= t_obs - 1e-12).sum())) / (boot + 1)


def covariance_interval(
    counts: np.ndarray, rng: np.random.Generator, boot: int, level: float = 0.95
) -> tuple[float, float]:
    """Percentile bootstrap interval for c from multinomial resamples of the table."""

    n = int(counts.sum())
    sims = rng.multinomial(n, counts / n, size=boot)
    _, _, c = estimates(sims)
    lo, hi = np.quantile(c, [(1 - level) / 2, (1 + level) / 2])
    return float(lo), float(hi)


def holm(pvalues: list[float], alpha: float = ALPHA) -> tuple[list[bool], list[float]]:
    """Holm (1979) step-down: rejections and adjusted p-values, in input order."""

    m = len(pvalues)
    order = sorted(range(m), key=lambda i: (pvalues[i], i))
    adjusted = [0.0] * m
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvalues[i]))
        adjusted[i] = running
    reject = [adjusted[i] <= alpha for i in range(m)]
    return reject, adjusted
