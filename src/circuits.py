"""Target and probe circuits for protocol v3 (Sections 2.2, 2.4, 6.2).

Circuits are compiled once with Qiskit (basis ``rz,sx,x,cx``, identity layout,
routing ``none``, optimization level 0, derived ``seed_transpiler``) and then
represented as a plain operation list ``(name, qubits, params)`` that the exact
simulator in ``simulate.py`` executes.  Every interpretation of protocol text
used here is listed in ``docs/part2/execution_contract_v3.md``.

Logical QAOA layer convention: cost layer ``RZZ(gamma)`` on every edge in
lexicographic order, then mixer ``RX(2*beta)`` on every qubit.  The initial
state is ``H`` on every qubit.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass

Op = tuple[str, tuple[int, ...], tuple[float, ...]]

BASIS = ("rz", "sx", "x", "cx")
HARD = "cx"


@dataclass(frozen=True)
class Compiled:
    name: str
    width: int
    ops: tuple[Op, ...]

    @property
    def hard_count(self) -> int:
        return sum(op[0] == HARD for op in self.ops)

    def sha256(self) -> str:
        payload = json.dumps([self.width, self.ops], sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _logical(width, edges, gammas, betas, epsilon=0.0):
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(width)
    qc.h(range(width))
    for layer, (gamma, beta) in enumerate(zip(gammas, betas, strict=True)):
        for i, j in edges:
            qc.rzz((1.0 + epsilon) * gamma, i, j)
        qc.barrier(label=f"cost{layer}")
        for q in range(width):
            qc.rx(2.0 * beta, q)
    return qc


def _ops_from_qiskit(circuit) -> list[Op]:
    ops: list[Op] = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = tuple(circuit.find_bit(q).index for q in instruction.qubits)
        params = tuple(float(p) for p in instruction.operation.params)
        if name == "barrier":
            ops.append(("barrier", qubits, ()))
            continue
        if name not in BASIS:
            raise AssertionError(f"non-basis gate after transpilation: {name}")
        ops.append((name, qubits, params))
    return ops


def compile_target(
    width: int,
    edges: Sequence[tuple[int, int]],
    candidate: dict,
    seed_transpiler: int,
    epsilon: float = 0.0,
) -> Compiled:
    """Compile one candidate.  ``epsilon`` implements E2 at the logical RZZ level."""

    from qiskit import transpile

    logical = _logical(width, edges, candidate["gamma"], candidate["beta"], epsilon)
    compiled = transpile(
        logical,
        basis_gates=list(BASIS),
        initial_layout=list(range(width)),
        routing_method="none",
        optimization_level=0,
        seed_transpiler=seed_transpiler,
    )
    ops = _ops_from_qiskit(compiled)
    if candidate.get("identity_pairs"):
        ops = insert_identity_pairs(ops, edges[0])
    barriers = sum(op[0] == "barrier" for op in ops)
    if barriers != len(candidate["gamma"]):
        raise AssertionError("cost-layer barriers did not survive transpilation")
    return Compiled("target", width, tuple(ops))


def insert_identity_pairs(ops: Sequence[Op], edge: tuple[int, int]) -> list[Op]:
    """Insert ``CX-CX`` on ``edge`` immediately after every cost-layer barrier."""

    out: list[Op] = []
    inserted = 0
    for op in ops:
        out.append(op)
        if op[0] == "barrier":
            out.append((HARD, tuple(edge), ()))
            out.append((HARD, tuple(edge), ()))
            inserted += 1
    if inserted == 0:
        raise AssertionError("no cost-layer barrier found for identity pairs")
    return out


def assert_identity_pairs(
    compiled: Compiled, edge: tuple[int, int], layers: int
) -> None:
    ops = compiled.ops
    found = 0
    for index, op in enumerate(ops[:-2]):
        if (
            op[0] == "barrier"
            and ops[index + 1] == (HARD, tuple(edge), ())
            and ops[index + 2] == (HARD, tuple(edge), ())
        ):
            found += 1
    if found != layers:
        raise AssertionError(f"identity pairs found {found}, expected {layers}")


# ---------------------------------------------------------------- probe forms


def _inverse(op: Op) -> list[Op]:
    name, qubits, params = op
    if name == "rz":
        return [("rz", qubits, (-params[0],))]
    if name in ("x", "cx"):
        return [op]
    if name == "sx":
        return [("sxdg", qubits, ())]
    raise ValueError(f"no inverse for {name}")


def fold(compiled: Compiled, scale: int = 3) -> Compiled:
    """Local unitary folding of every gate: G -> G (G^dagger G)^((scale-1)/2)."""

    if scale % 2 != 1 or scale < 1:
        raise ValueError("scale must be an odd positive integer")
    out: list[Op] = []
    for op in compiled.ops:
        out.append(op)
        if op[0] == "barrier":
            continue
        for _ in range((scale - 1) // 2):
            out.extend(_inverse(op))
            out.append(op)
    return Compiled(f"fold{scale}", compiled.width, tuple(out))


def nearest_clifford_angle(theta: float) -> float:
    """Nearest multiple of pi/2; exact half ties go toward the smaller angle."""

    quarter = math.pi / 2
    k = theta / quarter
    lower = math.floor(k)
    k_rounded = lower if (k - lower) <= 0.5 else lower + 1
    return k_rounded * quarter


def clifford_twin(compiled: Compiled) -> Compiled:
    ops = [
        ("rz", op[1], (nearest_clifford_angle(op[2][0]),)) if op[0] == "rz" else op
        for op in compiled.ops
    ]
    return Compiled("twin", compiled.width, tuple(ops))


def _sylvester_hadamard(order: int = 16) -> list[list[int]]:
    h = [[1]]
    while len(h) < order:
        h = [row + row for row in h] + [row + [-x for x in row] for row in h]
    return h


def frame_rows(width: int) -> list[tuple[int, ...]]:
    """16 rows of a strength-2 binary orthogonal array, one column per qubit.

    Columns are distinct non-constant columns of the 16x16 Sylvester-Hadamard
    matrix (columns 1..width), mapped +1 -> 0 and -1 -> 1.  Any two such
    columns are orthogonal, so every pair of qubits sees each of the four sign
    combinations exactly four times.
    """

    if not 1 <= width <= 15:
        raise ValueError("width must be between 1 and 15")
    h = _sylvester_hadamard(16)
    return [
        tuple(0 if h[r][c] == 1 else 1 for c in range(1, width + 1)) for r in range(16)
    ]


def framed(compiled: Compiled, row: Sequence[int]) -> Compiled:
    """Logically equivalent version with a static X frame around every hard gate.

    Before each ``CX(c,t)`` apply ``X^a_c X^a_t`` from the frame row; after it
    apply the conjugated Pauli ``CX (X^a_c X^a_t) CX = X^a_c X^(a_c xor a_t)_t``
    so the logical unitary is unchanged.
    """

    out: list[Op] = []
    for op in compiled.ops:
        if op[0] != HARD:
            out.append(op)
            continue
        c, t = op[1]
        a_c, a_t = row[c], row[t]
        if a_c:
            out.append(("x", (c,), ()))
        if a_t:
            out.append(("x", (t,), ()))
        out.append(op)
        if a_c:
            out.append(("x", (c,), ()))
        if a_c ^ a_t:
            out.append(("x", (t,), ()))
    return Compiled("frame", compiled.width, tuple(out))


def preparation(width: int, bits: dict[int, int], name: str) -> Compiled:
    """Basis-state preparation circuit for P4a/P4b (X on qubits prepared in 1)."""

    ops = tuple(("x", (q,), ()) for q in range(width) if bits.get(q, 0))
    return Compiled(name, width, ops)
