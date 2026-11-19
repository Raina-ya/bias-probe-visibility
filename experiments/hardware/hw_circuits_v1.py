"""Circuits, bit ordering and qubit selection for the hardware readout amendment v1.

Two P4a circuits on WIDTH logical qubits: ``p4a_all0`` (no gates) and
``p4a_all1`` (X on every qubit).  Logical qubit k is measured into classical
bit k of the register named ``c``.

Bit ordering (amendment Section 5.2).  Qiskit count keys are little-endian:
the rightmost character is classical bit 0.  The internal order used by the
analysis is big-endian in the logical index, as in ``src/simulate.py``:
character k is logical qubit k.  ``qiskit_key_to_internal`` is the only
conversion; it reverses the key.  Verified on Qiskit's BasicSimulator in
``tests/test_hw_readout_v1.py`` and on the IBM runtime local mode in
``experiments/hardware/hw_adapter_smoke_v1.py``.

Logical-to-physical layout.  ``select_qubits`` returns physical qubits in
selection order; logical qubit k runs on the k-th selected physical qubit.
``verify_layout`` checks this on the transpiled circuit.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

WIDTH = 8
REGISTER = "c"
CIRCUITS = ("p4a_all0", "p4a_all1")
PREPARED_BIT = {"p4a_all0": 0, "p4a_all1": 1}
TRANSPILE_SEED = 20261111


def build_logical(name: str, width: int = WIDTH):
    """Return the logical circuit ``name`` (Qiskit QuantumCircuit)."""

    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    if name not in PREPARED_BIT:
        raise ValueError(f"unknown circuit {name}")
    q = QuantumRegister(width, "q")
    c = ClassicalRegister(width, REGISTER)
    qc = QuantumCircuit(q, c, name=name)
    if PREPARED_BIT[name]:
        qc.x(q)
    qc.barrier(q)
    for k in range(width):
        qc.measure(q[k], c[k])
    return qc


def qiskit_key_to_internal(key: str, width: int = WIDTH) -> str:
    """Little-endian Qiskit key -> internal string whose character k is logical qubit k."""

    key = key.replace(" ", "")
    if len(key) != width or set(key) - {"0", "1"}:
        raise ValueError(f"unexpected count key {key!r}")
    return key[::-1]


def internal_counts(counts: Mapping[str, int], width: int = WIDTH) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, n in counts.items():
        z = qiskit_key_to_internal(key, width)
        out[z] = out.get(z, 0) + int(n)
    return out


def flip_pattern(internal_key: str, circuit: str) -> str:
    """Flip bits (1 = outcome differs from the prepared bit) for one internal key."""

    prepared = str(PREPARED_BIT[circuit])
    return "".join("0" if b == prepared else "1" for b in internal_key)


def pair_table(counts: Mapping[str, int], circuit: str, i: int, j: int) -> list[int]:
    """Flip table (n00, n01, n10, n11) of logical qubits i < j from internal counts."""

    if not i < j:
        raise ValueError("pair must satisfy i < j")
    table = [0, 0, 0, 0]
    for z, n in counts.items():
        f = flip_pattern(z, circuit)
        table[2 * int(f[i]) + int(f[j])] += int(n)
    return table


def select_qubits(
    readout_error: Mapping[int, float],
    edges: Iterable[Sequence[int]],
    width: int = WIDTH,
) -> list[int]:
    """Greedy connected selection of ``width`` physical qubits (amendment Section 5.2).

    Start from the qubit with the smallest reported readout error, then
    repeatedly add the neighbour of the selected set with the smallest reported
    readout error.  Ties go to the lower index.  Qubits without a reported
    readout error are never selected.
    """

    usable = {int(q): float(e) for q, e in readout_error.items() if e is not None}
    neighbours: dict[int, set[int]] = {q: set() for q in usable}
    for a, b in edges:
        a, b = int(a), int(b)
        if a in usable and b in usable and a != b:
            neighbours[a].add(b)
            neighbours[b].add(a)
    if len(usable) < width:
        raise ValueError("fewer usable qubits than the width")
    key = lambda q: (usable[q], q)  # noqa: E731
    chosen = [min(usable, key=key)]
    while len(chosen) < width:
        frontier = set().union(*(neighbours[q] for q in chosen)) - set(chosen)
        if not frontier:
            raise ValueError("no connected set of the requested width")
        chosen.append(min(frontier, key=key))
    return chosen


def verify_layout(transpiled, physical: Sequence[int], width: int = WIDTH) -> None:
    """Raise unless each measurement maps physical[k] to classical bit k of ``c``.

    Also requires exactly ``width`` measurements and, in ``p4a_all1``, one X on
    each selected qubit before its measurement.
    """

    measured: dict[int, int] = {}
    x_on: set[int] = set()
    for inst in transpiled.data:
        name = inst.operation.name
        if name == "measure":
            q = transpiled.find_bit(inst.qubits[0]).index
            reg_bit = transpiled.find_bit(inst.clbits[0])
            regs = [(r.name, i) for r, i in reg_bit.registers]
            k = [i for r, i in regs if r == REGISTER]
            if len(k) != 1:
                raise ValueError("measurement outside register c")
            measured[q] = k[0]
        elif name == "x":
            x_on.add(transpiled.find_bit(inst.qubits[0]).index)
        elif name not in ("barrier", "delay"):
            raise ValueError(f"unexpected operation {name} in transpiled circuit")
    expected = {int(physical[k]): k for k in range(width)}
    if measured != expected:
        raise ValueError(f"layout mismatch: measured {measured}, expected {expected}")
    if transpiled.name == "p4a_all1" and x_on != set(expected):
        raise ValueError("p4a_all1 must apply X to every selected qubit")
    if transpiled.name == "p4a_all0" and x_on:
        raise ValueError("p4a_all0 must not apply X")
