"""Design check: attainable harmful-bias ratios for the readout structures.

Evidence type: noiseless simulation (exact statevectors and exact readout
channels; no shots).  Graphs and candidates come from the ``software_test``
namespace (split 99), never from development or holdout seeds, so this check
does not instantiate a locked split and does not touch protocol data.

For each graph it computes the exact ideal gap g and, for the strongest
readout setting in each structure, the signed harmful ratio
``beta/Delta = (g_noisy - g) * sign(g) / |g|`` (negative means the observed gap
moves toward a flipped decision).  It also records max |<Z_i>| to check the
global bit-flip symmetry of QAOA-MaxCut states.
"""

from __future__ import annotations

import argparse
import itertools
import platform
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import manifest  # noqa: E402


def qaoa_probabilities(width, edges, gammas, betas):
    size = 2**width
    bits = (np.arange(size)[:, None] >> np.arange(width)[::-1]) & 1
    cut = np.zeros(size)
    for i, j in edges:
        cut += bits[:, i] != bits[:, j]
    psi = np.full(size, 1 / np.sqrt(size), dtype=complex)
    for gamma, beta in zip(gammas, betas, strict=True):
        psi = psi * np.exp(-1j * gamma * cut)
        tensor = psi.reshape([2] * width)
        mixer = np.array(
            [[np.cos(beta), -1j * np.sin(beta)], [-1j * np.sin(beta), np.cos(beta)]]
        )
        for qubit in range(width):
            tensor = np.moveaxis(
                np.tensordot(mixer, tensor, axes=([1], [qubit])), 0, qubit
            )
        psi = tensor.reshape(size)
    return np.abs(psi) ** 2, bits, cut / len(edges)


def tensor_readout(probabilities, width, rates):
    tensor = probabilities.reshape([2] * width)
    for qubit, (p10, p01) in enumerate(rates):
        channel = np.array([[1 - p10, p01], [p10, 1 - p01]])
        tensor = np.moveaxis(
            np.tensordot(channel, tensor, axes=([1], [qubit])), 0, qubit
        )
    return tensor.reshape(-1)


def correlated_flips(probabilities, width, qubits, marginal, tau):
    patterns = list(itertools.product((0, 1), repeat=len(qubits)))
    weights = [
        np.prod([marginal if flip else 1 - marginal for flip in pattern])
        + tau * (-1) ** sum(pattern)
        for pattern in patterns
    ]
    if min(weights) < 0:
        raise ValueError("invalid flip-pattern distribution")
    tensor = probabilities.reshape([2] * width)
    result = np.zeros_like(tensor)
    for pattern, weight in zip(patterns, weights, strict=True):
        shifted = tensor
        for qubit, flip in zip(qubits, pattern, strict=True):
            if flip:
                shifted = np.flip(shifted, axis=qubit)
        result = result + weight * shifted
    return result.reshape(-1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "experiments" / "design_checks" / "readout_ratio_log.txt",
    )
    args = parser.parse_args()
    if args.output.exists():
        print(f"Refusing to overwrite existing output: {args.output}")
        return 1
    records = manifest.build_manifest("software_test", REPO)
    ratios = {"E4": [], "E5": [], "E5-prime": [], "E6": []}
    max_z = 0.0
    ties = 0
    for record in records:
        width = record.width
        probs = []
        score = None
        for candidate in record.candidates:
            p, bits, score = qaoa_probabilities(
                width, record.edges, candidate["gamma"], candidate["beta"]
            )
            probs.append(p)
            max_z = max(max_z, float(np.abs(p @ (1 - 2 * bits)).max()))
        gap = probs[0] @ score - probs[1] @ score
        if abs(gap) <= 1e-12:
            ties += 1
            continue

        def ratio(channel, gap=gap, probs=probs, score=score):
            noisy = channel(probs[0]) @ score - channel(probs[1]) @ score
            return (noisy - gap) * np.sign(gap) / abs(gap)

        ratios["E4"].append(
            ratio(lambda p, w=width: tensor_readout(p, w, [(0.08, 0.12)] * w))
        )
        ratios["E5"].append(
            min(
                ratio(
                    lambda p, w=width, t=tau, r=record: correlated_flips(
                        p, w, r.first_edge, 0.10, t
                    )
                )
                for tau in (-0.01, 0.01)
            )
        )
        ratios["E5-prime"].append(
            min(
                ratio(
                    lambda p, w=width, t=tau, r=record: correlated_flips(
                        p, w, r.first_connected_triple, 0.25, t
                    )
                )
                for tau in (-0.015625, 0.015625)
            )
        )
        # E6 worst endpoint of the strongest drift: e0=0.04+0.03, e1=0.06-0.03 at t=1.
        ratios["E6"].append(
            ratio(lambda p, w=width: tensor_readout(p, w, [(0.07, 0.03)] * w))
        )

    lines = [
        "Readout ratio design check (noiseless simulation; software_test split 99 only)",
        f"graphs={len(records)} exact_ideal_ties={ties}",
        f"max_abs_single_qubit_Z={max_z:.3e}",
    ]
    for name, values in ratios.items():
        values = np.array(values)
        lines.append(
            f"{name}: min={values.min():.4f} median={np.median(values):.4f} "
            f"max={values.max():.4f} fraction_le_minus1={np.mean(values <= -1):.4f} "
            f"fraction_le_minus1.25={np.mean(values <= -1.25):.4f}"
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
