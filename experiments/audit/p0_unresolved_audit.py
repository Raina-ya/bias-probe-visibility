"""Pre-data audit of v3 P0 cells (population level, split 99 only).

Evidence type: noiseless/exact-channel population computation plus a Gaussian
approximation of the sampling distribution of the target gap.  No shot is
drawn.  For each graph and structure at its v3 main setting, P(L_T <= 0) is
computed from the exact noisy mean gap and the exact per-shot score variances
at n_A = n_B = 8192, then averaged over graphs (the P0 "power" of Section 11.1).
"""

from __future__ import annotations

import argparse
import math
import platform
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import channels  # noqa: E402
import execution  # noqa: E402
import manifest  # noqa: E402
import simulate  # noqa: E402

N_EACH = 8192
H = math.sqrt(math.log(4 / 0.025) / (2 * N_EACH))
MAIN = {
    "E0": ["0.0"],
    "E1": ["0.04"],
    "E2": ["-0.04", "0.04"],
    "E3": ["-0.04", "0.04"],
    "E4": ["(0.08,0.12)"],
    "E5": ["-0.01", "0.01"],
    "E5'": ["-0.015625", "0.015625"],
    "E6": ["-0.03", "0.03"],
}


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def post_distribution(record, condition, cache, circuit):
    pre = cache.get(circuit, condition.gate)
    if condition.readout_kind == "e6":
        parts = [
            channels.apply_readout(
                pre,
                record.width,
                channels.readout_for(
                    condition,
                    record.width,
                    record.first_edge,
                    record.first_connected_triple,
                    execution.block_time(b),
                ),
            )
            for b in range(8)
        ]
        return np.mean(parts, axis=0)
    readout = channels.readout_for(
        condition, record.width, record.first_edge, record.first_connected_triple
    )
    return channels.apply_readout(pre, record.width, readout)


def unresolved_probability(record, structure, setting, cache):
    condition = channels.parse_condition(structure, setting)
    scores = simulate.cut_scores(record.width, record.edges)
    targets = execution.target_circuits("software_test", record, condition)
    means, variances = [], []
    for circuit in targets:
        p = post_distribution(record, condition, cache, circuit)
        m = float(p @ scores)
        means.append(m)
        variances.append(float(p @ scores**2) - m * m)
    mu = means[0] - means[1]
    sigma = math.sqrt(variances[0] / N_EACH + variances[1] / N_EACH)
    if sigma == 0:
        return float(abs(mu) <= 2 * H), mu
    return phi((2 * H - mu) / sigma) - phi((-2 * H - mu) / sigma), mu


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "experiments" / "audit" / "p0_unresolved_log.txt",
    )
    args = parser.parse_args()
    if args.output.exists():
        print(f"Refusing to overwrite existing output: {args.output}")
        return 1
    records = manifest.build_manifest("software_test", REPO)
    cache = execution.SolveCache()
    lines = [
        "P0 unresolved audit (population level + Gaussian approximation; split 99 only)",
        f"graphs={len(records)} n_each={N_EACH} hoeffding_half_width_sum={2 * H:.6f}",
    ]
    for structure, settings in MAIN.items():
        rates = {}
        for setting in settings:
            values = [
                unresolved_probability(r, structure, setting, cache)[0] for r in records
            ]
            rates[setting] = float(np.mean(values))
        low = min(rates.values())
        label = (
            "visible-range" if low >= 0.80 else ("blind" if low <= 0.10 else "partial")
        )
        detail = " ".join(f"setting={k}:{v:.4f}" for k, v in rates.items())
        lines.append(
            f"{structure} {detail} min_over_signs={low:.4f} implied_label={label} "
            f"distance_from_blind_bound={low - 0.10:+.4f}"
        )
    lines += [
        f"python={sys.version.split()[0]}",
        f"platform={platform.platform()}",
        f"numpy={np.__version__}",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
