"""Readout channels and structure settings for protocol v3, Section 3.

Readout acts on exact pre-readout distributions.  Bit order follows
``simulate.py`` (qubit 0 is the most significant bit).
"""

from __future__ import annotations

import itertools
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from simulate import GateNoise

E0_VALUES = (0.0, 0.01, -0.01, 0.02, -0.02, 0.04, -0.04)


@dataclass(frozen=True)
class Readout:
    """Per-qubit assignment rates plus an optional correlated flip block."""

    rates: tuple[tuple[float, float], ...]  # (Pr(1|0), Pr(0|1)) per qubit
    block_qubits: tuple[int, ...] = ()
    block_marginal: float = 0.0
    block_tau: float = 0.0


@dataclass(frozen=True)
class Condition:
    structure: str
    setting: str
    gate: GateNoise
    epsilon: float  # E2 logical RZZ scale error
    offset: float  # E0 common-mode offset
    readout_kind: str  # "none", "e4", "e5", "e5p", "e6"
    readout_params: tuple[float, ...]


def parse_condition(structure: str, setting: str) -> Condition:
    value = setting
    if structure == "E0":
        return Condition("E0", value, GateNoise(), 0.0, float(value), "none", ())
    if structure == "E1":
        return Condition(
            "E1", value, GateNoise(depolarizing=float(value)), 0.0, 0.0, "none", ()
        )
    if structure == "E2":
        return Condition("E2", value, GateNoise(), float(value), 0.0, "none", ())
    if structure == "E3":
        return Condition("E3", value, GateNoise(zz=float(value)), 0.0, 0.0, "none", ())
    if structure == "E4":
        a, b = (float(x) for x in value.strip("()").split(","))
        return Condition("E4", value, GateNoise(), 0.0, 0.0, "e4", (a, b))
    if structure == "E5":
        return Condition("E5", value, GateNoise(), 0.0, 0.0, "e5", (float(value),))
    if structure == "E5'":
        return Condition("E5'", value, GateNoise(), 0.0, 0.0, "e5p", (float(value),))
    if structure == "E6":
        return Condition("E6", value, GateNoise(), 0.0, 0.0, "e6", (float(value),))
    raise ValueError(f"unknown structure {structure}")


def readout_for(
    condition: Condition,
    width: int,
    first_edge: Sequence[int],
    first_triple: Sequence[int],
    t: float | None = None,
) -> Readout:
    kind = condition.readout_kind
    clean = tuple((0.0, 0.0) for _ in range(width))
    if kind == "none":
        return Readout(clean)
    if kind == "e4":
        a, b = condition.readout_params
        return Readout(tuple((a, b) for _ in range(width)))
    if kind == "e5":
        return Readout(clean, tuple(first_edge), 0.10, condition.readout_params[0])
    if kind == "e5p":
        return Readout(clean, tuple(first_triple), 0.25, condition.readout_params[0])
    if kind == "e6":
        if t is None:
            raise ValueError("E6 readout needs a block time")
        delta = condition.readout_params[0]
        return Readout(
            tuple((0.04 + delta * t, 0.06 - delta * t) for _ in range(width))
        )
    raise ValueError(kind)


def apply_readout(
    probabilities: np.ndarray, width: int, readout: Readout
) -> np.ndarray:
    tensor = probabilities.reshape([2] * width)
    for q, (p10, p01) in enumerate(readout.rates):
        if p10 == 0.0 and p01 == 0.0:
            continue
        m = np.array([[1 - p10, p01], [p10, 1 - p01]])
        tensor = np.moveaxis(np.tensordot(m, tensor, axes=([1], [q])), 0, q)
    if readout.block_qubits:
        k = len(readout.block_qubits)
        out = np.zeros_like(tensor)
        for pattern in itertools.product((0, 1), repeat=k):
            weight = float(
                np.prod(
                    [
                        readout.block_marginal if f else 1 - readout.block_marginal
                        for f in pattern
                    ]
                )
                + readout.block_tau * (-1) ** sum(pattern)
            )
            if weight < -1e-15:
                raise ValueError("invalid correlated flip distribution")
            shifted = tensor
            for q, flip in zip(readout.block_qubits, pattern, strict=True):
                if flip:
                    shifted = np.flip(shifted, axis=q)
            out = out + weight * shifted
        tensor = out
    result = tensor.reshape(-1)
    result[result < 0] = 0.0
    return result / result.sum()


def assignment_matrix(width: int, readout: Readout) -> np.ndarray:
    """Full 2^w x 2^w column-stochastic matrix (certificate enumeration)."""

    size = 2**width
    columns = [apply_readout(np.eye(size)[j], width, readout) for j in range(size)]
    return np.stack(columns, axis=1)
