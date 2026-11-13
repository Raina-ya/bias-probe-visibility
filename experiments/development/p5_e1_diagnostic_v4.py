"""Investigate the invariant-stratum disagreement P5/E1 in development (Task 2-3).

Protocol v4 Section 5.2: an invariant-stratum disagreement indicates an
implementation or derivation error.  The matrix derives P5/E1 as invariant
because two-qubit depolarizing noise commutes with the global bit flip, so the
pre-readout distribution stays complement-symmetric and the P5 statistic of
the *expected* counts is 0 under both E1 and its matched null.

This script separates the two explanations using development rows only:

1. Implementation check: if E1 were implemented with a symmetry-breaking
   error, pooled counts would be complement-asymmetric.  For each graph and
   candidate, the 32 repeats of E1 at the main point are pooled and a
   chi-square test of p(z) = p(not z) is run; under symmetry the p-values are
   uniform.
2. Finite-shot check: P5 is a plug-in statistic, 0.5 * sum |p_hat(z) -
   p_hat(not z)|, whose expectation under an exactly symmetric distribution is
   positive and depends on the distribution's shape.  Depolarization flattens
   the distribution, which can raise that expectation.  For every row, the
   counts are symmetrized and P5 is re-sampled 10 times from the symmetric
   multinomial with the row's own shot count; if the observed E1-minus-null
   shift in mean P5 equals the shift of these symmetric expectations, the
   disagreement is finite-shot plug-in bias under a symmetric population, not
   an implementation error.

The re-sampling uses SeedSequence([ROOT_SEED, 10, 7, 1, 50, 0, ...]) (split
10, artifact 7 bootstrap, structure E1, probe P5).  Output is descriptive and
changes no matrix label, probe, threshold, or rule (Section 16.3).
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import chi2

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import cells_v4  # noqa: E402
import probes  # noqa: E402
from hashing import canonical_sha256  # noqa: E402
from protocol_contract import ROOT_SEED  # noqa: E402

OUT = REPO / "results" / "development_v4"
REPORT = REPO / "docs" / "freeze" / "dev_mismatch_investigation_v4.md"
DRAWS = 10


def flip(z: str) -> str:
    return z.translate(str.maketrans("01", "10"))


def symmetric_expectation(counts: dict, rng) -> float:
    n = sum(counts.values())
    keys = sorted(set(counts) | {flip(z) for z in counts})
    p = np.array([(counts.get(z, 0) + counts.get(flip(z), 0)) / (2 * n) for z in keys])
    sims = []
    for _ in range(DRAWS):
        x = rng.multinomial(n, p / p.sum())
        sims.append(
            probes.complement_score(
                {k: int(v) for k, v in zip(keys, x, strict=True) if v}
            )
        )
    return float(np.mean(sims))


def symmetry_pvalue(counts: Counter) -> float:
    stat, df, seen = 0.0, 0, set()
    for z in sorted(counts):
        if z in seen:
            continue
        zb = flip(z)
        seen |= {z, zb}
        a, b = counts.get(z, 0), counts.get(zb, 0)
        if a + b:
            stat += (a - b) ** 2 / (a + b)
            df += 1
    return float(chi2.sf(stat, df))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--main-setting", default="0.04")
    args = parser.parse_args(argv)
    rng = np.random.default_rng(
        np.random.SeedSequence([ROOT_SEED, 10, 7, 1, 50, 0, 0, 0, 0, 0, 0])
    )
    want = {("main", args.main_setting), ("nulls", cells_v4.MATCHED_NULL["E1"])}
    observed, expected = defaultdict(list), defaultdict(list)
    pooled = defaultdict(Counter)
    shards = sorted((args.out / "nulls").glob("*.jsonl.gz")) + sorted(
        (args.out / "main").glob("*.jsonl.gz")
    )
    for path in shards:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                unit = json.loads(line)
                phase, probe, structure, setting, _, graph_id = unit["unit"]
                if probe != "P5" or structure != "E1" or (phase, setting) not in want:
                    continue
                for row in unit["rows"]:
                    if row["split"] != "development":
                        raise ValueError("non-development row")
                    obs, exp = [], []
                    for k, circuit in enumerate(row["circuits"]):
                        counts = circuit["counts"]
                        pooled[(phase, graph_id, k)].update(counts)
                        obs.append(probes.complement_score(counts))
                        exp.append(symmetric_expectation(counts, rng))
                    observed[phase].append(max(obs))
                    expected[phase].append(max(exp))
    pvalues = np.array(
        [symmetry_pvalue(c) for (ph, _, _), c in sorted(pooled.items()) if ph == "main"]
    )
    mo = {ph: float(np.mean(v)) for ph, v in observed.items()}
    me = {ph: float(np.mean(v)) for ph, v in expected.items()}
    shift_obs = mo["main"] - mo["nulls"]
    shift_exp = me["main"] - me["nulls"]
    lines = [
        "# Investigation of the invariant-stratum disagreement P5/E1 (development)",
        "",
        "Evidence type: noisy simulation, development split 10 only, plus a",
        "parametric re-sampling diagnostic. This document changes no matrix label,",
        "probe, threshold, or rule (protocol v4 Section 16.3).",
        "",
        "## Implementation check: is the E1 population complement-symmetric?",
        "",
        f"Pooled over 32 repeats, {len(pvalues)} graph-candidate chi-square tests of",
        "`p(z)=p(not z)` at the E1 main point gave",
        f"minimum p = {pvalues.min():.4f}, fraction p < 0.05 = {(pvalues < 0.05).mean():.3f},",
        f"fraction p < 0.01 = {(pvalues < 0.01).mean():.3f}.",
        "Under exact symmetry these fractions are expected near 0.05 and 0.01.",
        "",
        "## Finite-shot check: plug-in bias of P5 under a symmetric population",
        "",
        "| Rows | Mean observed P5 | Mean P5 re-sampled from the symmetrized counts |",
        "|---|---:|---:|",
        f"| matched null (`p=0`), n={len(observed['nulls'])} | {mo['nulls']:.6f} | {me['nulls']:.6f} |",
        f"| E1 main (`p={args.main_setting}`), n={len(observed['main'])} | {mo['main']:.6f} | {me['main']:.6f} |",
        f"| shift, E1 minus null | {shift_obs:+.6f} | {shift_exp:+.6f} |",
        "",
        (
            f"The symmetric re-sampling reproduces {shift_exp / shift_obs:.2f} of the "
            "observed shift."
            if shift_obs
            else "The observed shift is zero."
        ),
        "",
        "## Reading",
        "",
        "If the symmetry tests are consistent with uniform p-values and the",
        "symmetric re-sampling reproduces the observed shift, the disagreement is",
        "not an implementation error. It is a derivation error in the scope of the",
        "invariant stratum: the matrix established invariance of the population",
        "statistic (P5 of the expected counts, the semantic-test quantity), but P5",
        "is a nonlinear plug-in statistic whose finite-shot expectation depends on",
        "the shape of a symmetric distribution, and depolarization changes that",
        "shape. Under Section 16.3 the matrix label stays `blind`; on the holdout",
        "this cell is scored against `blind` as registered.",
        "",
        "## Inputs (SHA-256)",
        "",
    ]
    lines += [
        f"- `{p.name}` ({p.parent.name}): `{canonical_sha256(p)}`" for p in shards
    ]
    lines.append("")
    with args.report.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
    print(
        json.dumps(
            {
                "symmetry_tests": len(pvalues),
                "frac_p_below_0.05": round(float((pvalues < 0.05).mean()), 3),
                "shift_observed": shift_obs,
                "shift_symmetric": shift_exp,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
