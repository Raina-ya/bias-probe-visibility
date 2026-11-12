"""Exact pre-readout probabilities for compiled circuits (no shots).

Gate noise hooks after every hard ``CX`` implement E1 (two-qubit
depolarizing, density matrix) and E3 (static coherent ``RZZ(zeta)`` on the
gate's own pair, state vector or density matrix).  Without depolarizing noise a
state vector is used; both engines agree on noiseless circuits (tested).
Qubit 0 is the most significant bit of the basis index, matching bit strings
``z_0 z_1 ... z_{w-1}``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from circuits import HARD, Compiled

SX = 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]])
SXDG = SX.conj().T
X = np.array([[0, 1], [1, 0]], dtype=complex)


def _rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-0.5j * theta), 0], [0, np.exp(0.5j * theta)]])


def single_qubit_matrix(name: str, params) -> np.ndarray:
    if name == "rz":
        return _rz(params[0])
    if name == "sx":
        return SX
    if name == "sxdg":
        return SXDG
    if name == "x":
        return X
    raise ValueError(name)


@dataclass(frozen=True)
class GateNoise:
    depolarizing: float = 0.0  # E1 p
    zz: float = 0.0  # E3 zeta (radians)

    @property
    def mixed(self) -> bool:
        return self.depolarizing > 0.0


def _bits(width: int) -> np.ndarray:
    return (np.arange(2**width)[:, None] >> np.arange(width)[::-1]) & 1


def _cx_permutation(width: int, control: int, target: int) -> np.ndarray:
    bits = _bits(width)
    source = bits.copy()
    source[:, target] ^= bits[:, control]
    return (source * (1 << np.arange(width)[::-1])).sum(axis=1)


class _Engine:
    def __init__(self, width: int, mixed: bool) -> None:
        self.w = width
        self.n = 2**width
        self.mixed = mixed
        self.z = 1 - 2 * _bits(width)
        self._perm: dict[tuple[int, int], np.ndarray] = {}
        state = np.zeros(self.n, dtype=complex)
        state[0] = 1.0
        self.state = np.outer(state, state.conj()) if mixed else state

    def single(self, matrix: np.ndarray, q: int) -> None:
        if not self.mixed:
            t = self.state.reshape([2] * self.w)
            t = np.moveaxis(np.tensordot(matrix, t, axes=([1], [q])), 0, q)
            self.state = t.reshape(self.n)
            return
        t = self.state.reshape([2] * (2 * self.w))
        t = np.moveaxis(np.tensordot(matrix, t, axes=([1], [q])), 0, q)
        t = np.moveaxis(
            np.tensordot(matrix.conj(), t, axes=([1], [self.w + q])), 0, self.w + q
        )
        self.state = t.reshape(self.n, self.n)

    def cx(self, c: int, t: int) -> None:
        key = (c, t)
        if key not in self._perm:
            self._perm[key] = _cx_permutation(self.w, c, t)
        p = self._perm[key]
        self.state = self.state[np.ix_(p, p)] if self.mixed else self.state[p]

    def zz_phase(self, i: int, j: int, angle: float) -> None:
        d = np.exp(-0.5j * angle * self.z[:, i] * self.z[:, j])
        if self.mixed:
            self.state = d[:, None] * self.state * d.conj()[None, :]
        else:
            self.state = d * self.state

    def depolarize(self, i: int, j: int, p: float) -> None:
        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ket = list(letters[: self.w])
        bra = list(letters[self.w : 2 * self.w])
        traced = bra.copy()
        traced[i], traced[j] = ket[i], ket[j]
        keep = [c for k, c in enumerate(ket) if k not in (i, j)] + [
            c for k, c in enumerate(bra) if k not in (i, j)
        ]
        t = self.state.reshape([2] * (2 * self.w))
        reduced = np.einsum(f"{''.join(ket)}{''.join(traced)}->{''.join(keep)}", t)
        identity = np.eye(4).reshape(2, 2, 2, 2) / 4
        mixed = np.einsum(
            f"{''.join(keep)},{ket[i]}{ket[j]}{bra[i]}{bra[j]}->{''.join(ket)}{''.join(bra)}",
            reduced,
            identity,
        )
        self.state = (1 - p) * self.state + p * mixed.reshape(self.n, self.n)

    def probabilities(self) -> np.ndarray:
        if self.mixed:
            p = np.real(np.diag(self.state)).copy()
        else:
            p = np.abs(self.state) ** 2
        p[p < 0] = 0.0
        return p / p.sum()


NO_GATE_NOISE = GateNoise()


def probabilities(circuit: Compiled, noise: GateNoise = NO_GATE_NOISE) -> np.ndarray:
    """Exact computational-basis distribution before readout."""

    engine = _Engine(circuit.width, noise.mixed)
    for name, qubits, params in circuit.ops:
        if name == "barrier":
            continue
        if name == HARD:
            c, t = qubits
            engine.cx(c, t)
            if noise.depolarizing:
                engine.depolarize(c, t, noise.depolarizing)
            if noise.zz:
                engine.zz_phase(c, t, noise.zz)
            continue
        engine.single(single_qubit_matrix(name, params), qubits[0])
    return engine.probabilities()


def cut_scores(width: int, edges) -> np.ndarray:
    """Normalized cut score s_G(z) for every basis index."""

    bits = _bits(width)
    cut = np.zeros(2**width)
    for i, j in edges:
        cut += bits[:, i] != bits[:, j]
    return cut / len(edges)


def bitstrings(width: int) -> list[str]:
    return [format(index, f"0{width}b") for index in range(2**width)]


def is_close_distribution(p: np.ndarray) -> bool:
    return bool(np.all(p >= 0) and math.isclose(float(p.sum()), 1.0, abs_tol=1e-12))
