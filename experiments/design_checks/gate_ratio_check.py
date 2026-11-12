"""Design check: attainable harmful-bias ratios for the gate structures E1-E3.

Evidence type: noiseless simulation (exact density matrices, no shots) on the
``software_test`` namespace (split 99) only.  Each cost-layer edge is compiled
as CX(i,j) RZ_j(theta) CX(i,j); candidate 1 adds a CX-CX pair on the first edge
after every cost layer.  E1 applies a two-qubit depolarizing channel after every
CX; E2 scales every cost angle by (1+epsilon); E3 applies RZZ(zeta) on the same
pair after every CX (a simplified reading of E3.1 used only for magnitudes).
The QAOA angle convention here is a design-check convention, not the Part 2
compilation contract.
"""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import manifest  # noqa: E402

GRIDS = {
    "E1": (0.0025, 0.005, 0.01, 0.02, 0.04),
    "E2": (-0.04, -0.02, -0.01, -0.005, 0.005, 0.01, 0.02, 0.04),
    "E3": (-0.04, -0.02, -0.01, -0.005, 0.005, 0.01, 0.02, 0.04),
}


class DensityMatrix:
    def __init__(self, width: int) -> None:
        self.w = width
        self.n = 2**width
        self.bits = (np.arange(self.n)[:, None] >> np.arange(width)[::-1]) & 1
        self.z = 1 - 2 * self.bits
        psi = np.full(self.n, 1 / np.sqrt(self.n))
        self.rho = np.outer(psi, psi).astype(complex)

    def phase(self, diagonal: np.ndarray) -> None:
        self.rho = diagonal[:, None] * self.rho * np.conj(diagonal)[None, :]

    def cx(self, control: int, target: int) -> None:
        source = self.bits.copy()
        source[:, target] ^= self.bits[:, control]
        index = (source * (1 << np.arange(self.w)[::-1])).sum(axis=1)
        self.rho = self.rho[np.ix_(index, index)]

    def single(self, unitary: np.ndarray, qubit: int) -> None:
        tensor = self.rho.reshape([2] * (2 * self.w))
        tensor = np.moveaxis(
            np.tensordot(unitary, tensor, axes=([1], [qubit])), 0, qubit
        )
        tensor = np.moveaxis(
            np.tensordot(unitary.conj(), tensor, axes=([1], [self.w + qubit])),
            0,
            self.w + qubit,
        )
        self.rho = tensor.reshape(self.n, self.n)

    def depolarize(self, i: int, j: int, p: float) -> None:
        if p == 0:
            return
        tensor = self.rho.reshape([2] * (2 * self.w))
        letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ket = list(letters[: self.w])
        bra = list(letters[self.w : 2 * self.w])
        bra_traced = bra.copy()
        bra_traced[i], bra_traced[j] = ket[i], ket[j]
        reduced_idx = [c for k, c in enumerate(ket) if k not in (i, j)] + [
            c for k, c in enumerate(bra) if k not in (i, j)
        ]
        reduced = np.einsum(
            f"{''.join(ket)}{''.join(bra_traced)}->{''.join(reduced_idx)}", tensor
        )
        identity = np.eye(4).reshape(2, 2, 2, 2) / 4
        out_idx = "".join(ket) + "".join(bra)
        mixed = np.einsum(
            f"{''.join(reduced_idx)},{ket[i]}{ket[j]}{bra[i]}{bra[j]}->{out_idx}",
            reduced,
            identity,
        )
        self.rho = (1 - p) * self.rho + p * mixed.reshape(self.n, self.n)

    def probabilities(self) -> np.ndarray:
        return np.real(np.diag(self.rho))


def cut_value(width, edges, candidate, structure, strength) -> float:
    state = DensityMatrix(width)

    def hard(i, j):
        state.cx(i, j)
        if structure == "E1":
            state.depolarize(i, j, strength)
        if structure == "E3":
            state.phase(np.exp(-0.5j * strength * state.z[:, i] * state.z[:, j]))

    for gamma, beta in zip(candidate["gamma"], candidate["beta"], strict=True):
        theta = gamma * (1 + strength) if structure == "E2" else gamma
        for i, j in edges:
            hard(i, j)
            state.phase(np.exp(-0.5j * theta * state.z[:, j]))
            hard(i, j)
        if candidate["identity_pairs"]:
            hard(*edges[0])
            hard(*edges[0])
        mixer = np.array(
            [[np.cos(beta), -1j * np.sin(beta)], [-1j * np.sin(beta), np.cos(beta)]]
        )
        for qubit in range(width):
            state.single(mixer, qubit)
    cut = np.zeros(state.n)
    for i, j in edges:
        cut += state.bits[:, i] != state.bits[:, j]
    return float(state.probabilities() @ cut / len(edges))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "experiments" / "design_checks" / "gate_ratio_log.txt",
    )
    args = parser.parse_args()
    if args.output.exists():
        print(f"Refusing to overwrite existing output: {args.output}")
        return 1
    records = manifest.build_manifest("software_test", REPO)
    ratios = {(s, x): [] for s, grid in GRIDS.items() for x in grid}
    ties = 0
    for record in records:
        ideal = [
            cut_value(record.width, record.edges, c, "none", 0.0)
            for c in record.candidates
        ]
        gap = ideal[0] - ideal[1]
        if abs(gap) <= 1e-12:
            ties += 1
            continue
        for structure, grid in GRIDS.items():
            for strength in grid:
                noisy = [
                    cut_value(record.width, record.edges, c, structure, strength)
                    for c in record.candidates
                ]
                ratios[(structure, strength)].append(
                    ((noisy[0] - noisy[1]) - gap) * np.sign(gap) / abs(gap)
                )
    lines = [
        "Gate ratio design check (noiseless density matrices; software_test split 99 only)",
        f"graphs={len(records)} exact_ideal_ties={ties}",
    ]
    for (structure, strength), values in ratios.items():
        values = np.array(values)
        lines.append(
            f"{structure} strength={strength:+.4f}: median={np.median(values):+.4f} "
            f"min={values.min():+.4f} fraction_le_minus1={np.mean(values <= -1):.4f}"
        )
    lines += [
        f"manifest_sha256={manifest.manifest_sha256(records)}",
        f"python={sys.version.split()[0]}",
        f"platform={platform.platform()}",
        f"numpy={np.__version__}",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
