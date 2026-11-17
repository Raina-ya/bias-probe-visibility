"""Task 3-3: Proposition-1 prediction test, protocol v4 Section 13.

Step 1 (this task): ``pilot`` (split 30) then ``predict`` writes
results/prop1/predictions.csv and stops.  Step 2 (``score``, split 31) refuses
until the predictions are committed and docs/freeze/registration_prop1_v4.json
records their independent timestamp and hash.

Decisions not fixed by the registered text, written down before split 30 is
instantiated (docs/part3/prop1_plan_v4.md):

* noise: E1 two-qubit depolarizing at the locked main point p = 0.04, no
  readout error;
* graphs: the 100 holdout graph identities (edges); candidates: K = 4
  independent QAOA candidates drawn in the split-30 namespace with the v4
  candidate distributions (gamma ~ U[0, 2 pi), beta ~ U[0, pi)), no identity
  pairs; the same candidate circuits are scored in split 31, which changes only
  the shot seeds;
* the anchor intervals that define "unstable attenuation" are the Bonferroni
  intervals of the anchor-versus-candidate intercept gaps;
* orthant probabilities: condition on one standardized gap, integrate the
  exact bivariate normal CDF (Owen's T) by Gauss-Legendre quadrature of orders
  128 and 256 (384 outer points); converged when the two agree within
  max(1e-8, 1e-8 * P);
* bootstrap percentiles use method "inverted_cdf", as in Section 11.1;
* a hit is a strictly lower empirical top-1 error rate over the 32 scoring
  repeats for the predicted method; an exact tie is a miss for either
  prediction; a selection is an error when the sampled maximum is not unique.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import ndtr, owens_t

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "holdout"))
sys.path.insert(0, str(REPO / "experiments" / "development"))

import circuits  # noqa: E402
import execution  # noqa: E402
import manifest as base  # noqa: E402
import protocol_contract as contract  # noqa: E402
import simulate  # noqa: E402
import split_guard_v4  # noqa: E402
from hashing import canonical_sha256  # noqa: E402

PILOT_SPLIT = "prop1_pilot"
SCORING_SPLIT = "prop1_scoring"
K = 4
SCALES = (1, 3, 5)
WEIGHTS = (13 / 12, 1 / 3, -5 / 12)
PILOT_BLOCKS = 32
PILOT_SHOTS = 4_096  # per method per block
SCORING_REPEATS = 32
SCORING_SHOTS = 16_384  # per method per repeat
NOISE = simulate.GateNoise(depolarizing=0.04)
STRUCTURE_CODE = execution.STRUCTURE_CODES["E1"]
BOOTSTRAP = 10_000
ALPHA_ANCHOR = 0.05
GL_ORDERS = (128, 256)
TOLERANCE = 1e-8
OUT = REPO / "results" / "prop1"
PREDICTIONS = OUT / "predictions.csv"
REGISTRATION = Path("docs/freeze/registration_prop1_v4.json")
FIELDS = (
    "graph_id,K,anchor_id,pilot_blocks,pilot_shots_raw,pilot_shots_zne,"
    "scoring_repeats,scoring_shots_raw,scoring_shots_zne,mu_raw,gamma_hat,a_hat,"
    "u_zne,l_zne,u_raw,l_raw,prediction,diagnostic_reason,root_seed,protocol_sha256"
).split(",")


# ---------------------------------------------------------------- circuits


def candidates(split_for_draw: str, record) -> list[dict]:
    out = []
    for k in range(K):
        rng = base.rng_for(
            split_for_draw,
            base.ARTIFACT_CANDIDATE,
            width=record.width,
            depth=record.depth,
            graph_index=record.graph_index,
            candidate_index=k,
        )
        gammas = rng.uniform(0.0, 2.0 * math.pi, size=record.depth)
        betas = rng.uniform(0.0, math.pi, size=record.depth)
        out.append(
            {
                "gamma": [float(x) for x in gammas],
                "beta": [float(x) for x in betas],
                "identity_pairs": False,
            }
        )
    return out


def candidate_circuits(record, draw_split: str = PILOT_SPLIT):
    """[[scale-1, fold3, fold5] for each candidate] (same circuits in both splits)."""

    out = []
    for k, cand in enumerate(candidates(draw_split, record)):
        target = circuits.compile_target(
            record.width,
            record.edges,
            cand,
            execution.transpiler_seed(draw_split, record, k),
        )
        out.append([target, circuits.fold(target, 3), circuits.fold(target, 5)])
    return out


def labels() -> tuple[list[str], list[str]]:
    raw = [f"raw_c{k}" for k in range(K)]
    zne = [f"zne_c{k}_s{s}" for k in range(K) for s in SCALES]
    return raw, zne


def shot_rng(split: str, record, repeat: int) -> np.random.Generator:
    key = contract.seed_key(
        split=split,
        artifact_code=execution.ARTIFACT_SHOTS,
        structure_code=STRUCTURE_CODE,
        probe_code=0,
        width=record.width,
        depth=record.depth,
        graph_index=record.graph_index,
        candidate_index=0,
        repeat_index=repeat,
        parameter_index=0,
        allow_holdout=True,  # access control is split_guard's job
    )
    return np.random.default_rng(np.random.SeedSequence(list(key)))


def draw_block(rng, probs, width: int, shots: int) -> dict[str, dict[str, int]]:
    """Counts for the 4 Raw and 12 ZNE circuits in frozen label order."""

    raw_labels, zne_labels = labels()
    raw_alloc = contract.split_even(shots, raw_labels)
    zne_alloc = contract.split_even(shots, zne_labels)
    counts = {}
    for k, label in enumerate(raw_labels):
        counts[label] = execution._counts(rng, probs[k][0], raw_alloc[label], width)
    for label in zne_labels:
        k, s = int(label[5]), SCALES.index(int(label.split("_s")[1]))
        counts[label] = execution._counts(rng, probs[k][s], zne_alloc[label], width)
    return counts


def estimates(counts: dict, score: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    def mean(c):
        n = sum(c.values())
        return sum(v * score[int(z, 2)] for z, v in c.items()) / n

    raw = np.array([mean(counts[f"raw_c{k}"]) for k in range(K)])
    zne = np.array(
        [
            sum(
                w * mean(counts[f"zne_c{k}_s{s}"])
                for w, s in zip(WEIGHTS, SCALES, strict=True)
            )
            for k in range(K)
        ]
    )
    return raw, zne


# ---------------------------------------------------------------- orthant


def bvn_cdf(h, k, r):
    """P(X <= h, Y <= k) for standard bivariate normals with correlation r (Owen 1956)."""

    h, k, r = np.broadcast_arrays(
        np.asarray(h, float), np.asarray(k, float), np.asarray(r, float)
    )
    s = np.sqrt(1 - r * r)
    with np.errstate(divide="ignore", invalid="ignore"):
        ah = (k - r * h) / (h * s)
        ak = (h - r * k) / (k * s)
    ah = np.where(h == 0, np.where(k - r * h >= 0, np.inf, -np.inf), ah)
    ak = np.where(k == 0, np.where(h - r * k >= 0, np.inf, -np.inf), ak)
    beta = np.where((h * k > 0) | ((h * k == 0) & (h + k >= 0)), 0.0, 0.5)
    return 0.5 * (ndtr(h) + ndtr(k)) - owens_t(h, ah) - owens_t(k, ak) - beta


def orthant3(mu: np.ndarray, cov: np.ndarray, order: int) -> np.ndarray:
    """P(Z <= mu), Z ~ N(0, cov), for stacks mu (R,3), cov (R,3,3).

    Conditions on the first standardized coordinate and integrates the exact
    bivariate normal CDF over z1 in [min(-9, x1 - 1), min(x1, 9)] with
    Gauss-Legendre quadrature of the given order (outer integration points).
    """

    sd = np.sqrt(np.einsum("rii->ri", cov))
    x = mu / sd
    c = cov / (sd[:, :, None] * sd[:, None, :])
    r12, r13, r23 = c[:, 0, 1], c[:, 0, 2], c[:, 1, 2]
    a2, a3 = np.sqrt(1 - r12**2), np.sqrt(1 - r13**2)
    rho = (r23 - r12 * r13) / (a2 * a3)
    lo = np.minimum(-9.0, x[:, 0] - 1.0)
    hi = np.maximum(np.minimum(x[:, 0], 9.0), lo)
    t, w = leggauss(order)
    z = lo[:, None] + (hi - lo)[:, None] * (t[None] + 1) / 2
    w = w[None] * (hi - lo)[:, None] / 2
    f = (
        np.exp(-z * z / 2)
        / math.sqrt(2 * math.pi)
        * bvn_cdf(
            (x[:, 1, None] - r12[:, None] * z) / a2[:, None],
            (x[:, 2, None] - r13[:, None] * z) / a3[:, None],
            rho[:, None],
        )
    )
    return (f * w).sum(axis=1)


def orthant_converged(mu, cov, chunk: int = 250):
    out, ok = np.empty(len(mu)), np.empty(len(mu), dtype=bool)
    for i in range(0, len(mu), chunk):
        sl = slice(i, i + chunk)
        lo, hi = (orthant3(mu[sl], cov[sl], n) for n in GL_ORDERS)
        out[sl] = hi
        ok[sl] = np.abs(hi - lo) <= np.maximum(TOLERANCE, TOLERANCE * np.abs(hi))
    return out, ok


def ridge(cov: np.ndarray) -> np.ndarray:
    tr = np.trace(cov, axis1=1, axis2=2)
    lam = np.where(tr > 0, 1e-8 * tr / 3, 1e-8)
    return cov + lam[:, None, None] * np.eye(3)[None]


# ---------------------------------------------------------------- prediction


def bootstrap_rng(record) -> np.random.Generator:
    key = contract.seed_key(
        split=PILOT_SPLIT,
        artifact_code=7,
        structure_code=STRUCTURE_CODE,
        probe_code=0,
        width=record.width,
        depth=record.depth,
        graph_index=record.graph_index,
        candidate_index=0,
        repeat_index=0,
        parameter_index=0,
    )
    return np.random.default_rng(np.random.SeedSequence(list(key)))


def gaps(values: np.ndarray, anchor: int) -> np.ndarray:
    """Anchor minus each other candidate (maximization), candidate order. (...,K)->(...,3)"""

    others = [k for k in range(K) if k != anchor]
    return values[..., [anchor]] - values[..., others]


def predict_graph(
    record, raw_blocks: np.ndarray, zne_blocks: np.ndarray, resamples: int = BOOTSTRAP
) -> dict:
    """raw_blocks, zne_blocks: (32, K) block estimates."""

    anchor = int(np.argmax(zne_blocks.mean(axis=0)))
    rng = bootstrap_rng(record)
    idx = rng.integers(0, PILOT_BLOCKS, size=(resamples, PILOT_BLOCKS))
    zne_means = zne_blocks[idx].mean(axis=1)  # (R,K)
    a = ALPHA_ANCHOR / 6
    pair_lower = {}
    for i in range(K):
        for j in range(i + 1, K):
            d = zne_means[:, i] - zne_means[:, j]
            lo, hi = np.percentile(
                d, [100 * a / 2, 100 * (1 - a / 2)], method="inverted_cdf"
            )
            pair_lower[(i, j)], pair_lower[(j, i)] = lo, -hi
    resolved = all(pair_lower[(anchor, j)] > 0 for j in range(K) if j != anchor)

    g_raw, g_zne = gaps(raw_blocks, anchor), gaps(zne_blocks, anchor)
    mu_raw, mu_zne = g_raw.mean(axis=0), g_zne.mean(axis=0)
    s_raw, s_zne = np.cov(g_raw, rowvar=False), np.cov(g_zne, rowvar=False)
    var_raw = np.diag(s_raw)
    gamma = np.where(
        var_raw > 0, np.diag(s_zne) / np.where(var_raw > 0, var_raw, 1), np.nan
    )
    a_hat = mu_raw / mu_zne
    stable = (
        resolved  # anchor-vs-candidate intervals exclude zero exactly when resolved
    )

    def risks(blocks):
        g = gaps(blocks[idx], anchor)  # (R,32,3)
        m = g.mean(axis=1)
        c = g - m[:, None, :]
        cov = np.einsum("rbi,rbj->rij", c, c) / (PILOT_BLOCKS - 1) / 4  # Sigma_scoring
        p, ok = orthant_converged(m, ridge(cov))
        return 1 - p, ok

    r_raw, ok_raw = risks(raw_blocks)
    r_zne, ok_zne = risks(zne_blocks)
    l_raw, u_raw = np.percentile(r_raw, [2.5, 97.5], method="inverted_cdf")
    l_zne, u_zne = np.percentile(r_zne, [2.5, 97.5], method="inverted_cdf")
    converged = bool(ok_raw.all() and ok_zne.all())

    if not resolved:
        prediction, reason = "raw", "unresolved_anchor"
    elif not stable:
        prediction, reason = "raw", "unstable_attenuation"
    elif np.any(var_raw <= 0):
        prediction, reason = "raw", "uncertified_raw_default"
    elif not converged:
        prediction, reason = "raw", "numerical_failure"
    elif u_zne < l_raw:
        prediction, reason = "zne", "zne_separated"
    elif u_raw < l_zne:
        prediction, reason = "raw", "raw_separated"
    else:
        prediction, reason = "raw", "uncertified_raw_default"
    return {
        "anchor_id": anchor,
        "mu_raw": mu_raw.tolist(),
        "gamma_hat": [None if math.isnan(x) else float(x) for x in gamma],
        "a_hat": a_hat.tolist(),
        "u_zne": float(u_zne),
        "l_zne": float(l_zne),
        "u_raw": float(u_raw),
        "l_raw": float(l_raw),
        "prediction": prediction,
        "diagnostic_reason": reason,
        "converged_fraction": float((ok_raw.mean() + ok_zne.mean()) / 2),
    }


# ---------------------------------------------------------------- phases


def records(split_source: str = "holdout"):
    import run_holdout_v4 as hold

    if split_source == "holdout":
        return hold.records_after_run(REPO)
    return hold.records_from_base(split_source)  # tests only (software_test)


def pilot_graph(record, cache, split: str = PILOT_SPLIT) -> dict:
    probs = [
        [cache.get(c, NOISE) for c in trio]
        for trio in candidate_circuits(record, split)
    ]
    blocks = []
    for b in range(PILOT_BLOCKS):
        blocks.append(
            draw_block(shot_rng(split, record, b), probs, record.width, PILOT_SHOTS)
        )
    return {"graph_id": record.graph_id, "split": split, "blocks": blocks}


def block_estimates(entry: dict, record) -> tuple[np.ndarray, np.ndarray]:
    score = simulate.cut_scores(record.width, record.edges)
    pairs = [estimates(b, score) for b in entry["blocks"]]
    return np.array([p[0] for p in pairs]), np.array([p[1] for p in pairs])


def check_ready_pilot() -> None:
    split_guard_v4.require_split(REPO, PILOT_SPLIT)
    if not split_guard_v4.marker_path(REPO, "holdout").is_file():
        raise SystemExit("refused: holdout not finalized")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("pilot", "predict", "score"))
    parser.add_argument("--commit", required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)
    import runner

    head = runner._git("rev-parse", "HEAD")
    dirty = runner._git("status", "--porcelain", "--untracked-files=no")
    if head != args.commit or dirty:
        print(f"refused: HEAD {head} != --commit or tracked files modified")
        return 2
    if args.phase == "score":
        import score_prop1_v4

        return score_prop1_v4.run(args)
    check_ready_pilot()
    recs = records()
    by_id = {r.graph_id: r for r in recs}
    protocol_hash = canonical_sha256(REPO / split_guard_v4.PROTOCOL)
    args.out.mkdir(parents=True, exist_ok=True)

    if args.phase == "pilot":
        mine = [
            r for k, r in enumerate(recs) if k % args.shard_count == args.shard_index
        ]
        path = (
            args.out
            / "pilot"
            / f"shard_{args.shard_index:04d}_of_{args.shard_count:04d}.jsonl.gz"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            print(f"exists, not rerun: {path}")
            return 0
        cache, lines, started = execution.SolveCache(), [], time.perf_counter()
        for r in mine:
            lines.append(json.dumps(pilot_graph(r, cache), sort_keys=True))
        with gzip.open(path, "xt", encoding="utf-8") as h:
            h.write("\n".join(lines) + "\n")
        log = {
            "event": "done",
            "phase": "pilot",
            "file": path.name,
            "graphs": len(mine),
            "seconds": time.perf_counter() - started,
            "sha256": canonical_sha256(path),
            "commit": args.commit,
            "numpy": np.__version__,
        }
        with (args.out / "run_log_prop1_v4.jsonl").open("a", encoding="utf-8") as h:
            h.write(json.dumps(log, sort_keys=True) + "\n")
        print(json.dumps(log))
        return 0

    # predict
    entries = {}
    for path in sorted((args.out / "pilot").glob("*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as h:
            for line in h:
                e = json.loads(line)
                entries[e["graph_id"]] = e
    if set(entries) != set(by_id):
        print(f"refused: pilot covers {len(entries)} of {len(by_id)} graphs")
        return 2
    rows, started = [], time.perf_counter()
    for r in recs:
        raw_b, zne_b = block_estimates(entries[r.graph_id], r)
        p = predict_graph(r, raw_b, zne_b)
        rows.append(
            {
                "graph_id": r.graph_id,
                "K": K,
                "anchor_id": p["anchor_id"],
                "pilot_blocks": PILOT_BLOCKS,
                "pilot_shots_raw": PILOT_BLOCKS * PILOT_SHOTS,
                "pilot_shots_zne": PILOT_BLOCKS * PILOT_SHOTS,
                "scoring_repeats": SCORING_REPEATS,
                "scoring_shots_raw": SCORING_REPEATS * SCORING_SHOTS,
                "scoring_shots_zne": SCORING_REPEATS * SCORING_SHOTS,
                "mu_raw": json.dumps(p["mu_raw"]),
                "gamma_hat": json.dumps(p["gamma_hat"]),
                "a_hat": json.dumps(p["a_hat"]),
                "u_zne": repr(p["u_zne"]),
                "l_zne": repr(p["l_zne"]),
                "u_raw": repr(p["u_raw"]),
                "l_raw": repr(p["l_raw"]),
                "prediction": p["prediction"],
                "diagnostic_reason": p["diagnostic_reason"],
                "root_seed": contract.ROOT_SEED,
                "protocol_sha256": protocol_hash,
            }
        )
    with (args.out / "predictions.csv").open("x", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    summary = {
        "graphs": len(rows),
        "predict_zne": sum(r["prediction"] == "zne" for r in rows),
        "reasons": {
            k: sum(r["diagnostic_reason"] == k for r in rows)
            for k in sorted({r["diagnostic_reason"] for r in rows})
        },
        "seconds": time.perf_counter() - started,
        "predictions_sha256": canonical_sha256(args.out / "predictions.csv"),
    }
    with (args.out / "run_log_prop1_v4.jsonl").open("a", encoding="utf-8") as h:
        h.write(
            json.dumps(
                {"event": "done", "phase": "predict", "commit": args.commit, **summary},
                sort_keys=True,
            )
            + "\n"
        )
    print(json.dumps(summary))
    print(
        "STOP: commit results/prop1/predictions.csv and register it on OSF before scoring."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
