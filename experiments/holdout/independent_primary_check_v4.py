"""Independent recomputation of the v4 primary endpoint from the raw holdout rows.

Separate code path from score_primary_v4.py and analysis_v4.py: target gaps
are recomputed from the recorded circuit counts and the graph edges, the
Hoeffding bound L_T is recomputed from its formula (alpha_T = 0.025), alarms
use the locked clean-E0 thresholds, and the bootstrap uses its own resampling
with an unrelated generator (seed 12345), so its interval is expected to agree
only approximately.  Diagnostic only; it does not replace the frozen scorer.

Usage (after the holdout has finalized):
  python experiments/holdout/independent_primary_check_v4.py [--root DIR]
"""

import csv
import gzip
import json
import math
import sys
from collections import defaultdict
import numpy as np
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(REPO / "src"),
    str(REPO / "experiments" / "holdout"),
    str(REPO / "experiments" / "development"),
]
import run_holdout_v4 as hold  # only for the guard-free manifest (edges)

U = (
    sys.argv[sys.argv.index("--root") + 1] if "--root" in sys.argv else str(REPO)
) + "/"
DES = {
    "E1": "P1",
    "E2": "P2",
    "E3": "P3",
    "E4": "P4a",
    "E5": "P4a",
    "E5'": "P4a",
    "E6": "P4a",
}
COMP = {("P4a", s): "assignment" for s in DES} | {("P4a", "E6"): "temporal_contrast"}
records = (
    hold.records_from_base("holdout")
    if "--root" in sys.argv
    else hold.records_after_run(REPO)
)
edges = {r.graph_id: r.edges for r in records}
taus = {}
for r in csv.DictReader(open(REPO / "results/development_v4/thresholds_v4.csv")):
    if r["null"] == "clean_e0" and r["alpha"] == "0.05":
        taus[(r["probe"], r["structure"], int(r["width"]), int(r["depth"]))] = float(
            r["tau"]
        )
ideal = {}
for r in csv.DictReader(
    open(U + "results/holdout_v4/reference/holdout_reference_v4.csv")
):
    if r["point"] == "main":
        g = float(r["ideal_gap"])
        ideal.setdefault(r["graph_id"], 0 if abs(g) <= 1e-12 else (1 if g > 0 else -1))


def score_mean(counts, E):
    n = sum(counts.values())
    return sum(
        c * sum(z[i] != z[j] for i, j in E) / len(E) for z, c in counts.items()
    ) / n, n


need = {("P0", s) for s in DES} | {(DES[s], s) for s in DES}
cert = defaultdict(dict)
win = defaultdict(dict)
maxdiff = 0.0
lt_disagree = 0
for k in range(4):
    for line in gzip.open(
        U + f"results/holdout_v4/main/shard_{k:04d}_of_0004.jsonl.gz", "rt"
    ):
        e = json.loads(line)
        _, p, s, _, _, g = e["unit"]
        if (p, s) not in need:
            continue
        w, d = int(g.split("-")[1][1:]), int(g.split("-")[2][1:])
        for row in e["rows"]:
            pooled = defaultdict(dict)
            for c in row["circuits"]:
                if c["role"] != "target":
                    continue
                for z, v in c["counts"].items():
                    pooled[c["label"]][z] = pooled[c["label"]].get(z, 0) + v
            (ma, na), (mb, nb) = (
                score_mean(pooled["target0"], edges[g]),
                score_mean(pooled["target1"], edges[g]),
            )
            gap = ma - mb
            maxdiff = max(maxdiff, abs(gap - row["components"]["gap_target"]))
            L = (
                abs(gap)
                - math.sqrt(math.log(4 / 0.025) / (2 * na))
                - math.sqrt(math.log(4 / 0.025) / (2 * nb))
            )
            ok = L > 0
            lt_disagree += ok == row["alarm_p0"]
            if p != "P0":
                v = (
                    row["components"][COMP[(p, s)]]
                    if (p, s) in COMP
                    else row["statistic"]
                )
                ok = ok and not (v > taus[(p, s, w, d)])
            cert[(p, s)][(g, row["repeat"])] = ok
            win[(p, s)][(g, row["repeat"])] = 1 if gap > 0 else (-1 if gap < 0 else 0)
print(
    "max |gap recomputed - recorded| =",
    maxdiff,
    "; rows where own L_T>0 disagrees with recorded alarm_p0:",
    lt_disagree,
)
G = sorted(ideal, key=lambda g: tuple(int(x[1:]) for x in g.split("-")[1:]))
fc0 = {}
fc1 = {}
for s in DES:
    for p, store in (("P0", fc0), (DES[s], fc1)):
        store[s] = np.array(
            [
                [
                    cert[(p, s)][(g, r)]
                    and (win[(p, s)][(g, r)] != ideal[g] or ideal[g] == 0)
                    for r in range(32)
                ]
                for g in G
            ]
        )
    c0 = np.mean(list(cert[("P0", s)].values()))
    c1 = np.mean(list(cert[(DES[s], s)].values()))
    print(
        s, "FC0 %.6f FC1 %.6f C0 %.4f C1 %.4f" % (fc0[s].mean(), fc1[s].mean(), c0, c1)
    )
diff = np.mean([fc0[s].astype(float) - fc1[s] for s in DES], axis=0)
print(
    "dFC point %.6f" % diff.mean(), "pooled FC0 %.6f" % np.mean([fc0[s] for s in DES])
)
strata = defaultdict(list)
for i, g in enumerate(G):
    strata[g.split("-g")[0]].append(i)
rng = np.random.default_rng(12345)
per_graph = diff.mean(axis=1)
fcg = np.mean([fc0[s] for s in DES], axis=0).mean(axis=1)
bd, bf = [], []
for _ in range(10000):
    idx = np.concatenate([rng.choice(m, len(m)) for m in strata.values()])
    bd.append(per_graph[idx].mean())
    bf.append(fcg[idx].mean())
print(
    "own bootstrap dFC [%.6f, %.6f]  FC0 upper %.6f"
    % (*np.percentile(bd, [2.5, 97.5]), np.percentile(bf, 97.5))
)
