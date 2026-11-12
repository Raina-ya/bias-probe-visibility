"""Graph and candidate manifests for protocol v2, Section 2.

Everything here is outcome-free: graphs and QAOA parameter vectors only.  No
circuit is simulated, no ideal value is computed, and no shot is drawn.

Graph generators are implemented directly on NumPy ``Generator`` streams
rather than through a third-party graph library, so the manifest depends only
on NumPy's documented ``SeedSequence``/``PCG64`` behaviour.  The Watts-Strogatz
and Barabasi-Albert procedures follow the standard constructions (ring lattice
with per-edge rewiring; star seed graph with preferential attachment through a
repeated-node list).

Interpretations that the protocol text leaves implicit are listed in
``IMPLEMENTATION_NOTES`` and must be approved by the owner before the lock.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import protocol_contract as contract  # noqa: E402
import split_guard  # noqa: E402


FAMILIES = ("erdos_renyi", "watts_strogatz", "barabasi_albert")
GRAPHS_PER_STRATUM = {"development": 2, "holdout": 4, "software_test": 2}
FAMILY_TOTALS = {
    "development": {"erdos_renyi": 17, "watts_strogatz": 17, "barabasi_albert": 16},
    "holdout": {"erdos_renyi": 34, "watts_strogatz": 33, "barabasi_albert": 33},
    "software_test": {"erdos_renyi": 17, "watts_strogatz": 17, "barabasi_albert": 16},
}
CANDIDATES = 2
MAX_GRAPH_ATTEMPTS = 1_000
ARTIFACT_FAMILY = 1
ARTIFACT_GRAPH = 2
ARTIFACT_CANDIDATE = 3
NOT_APPLICABLE = 0

IMPLEMENTATION_NOTES = (
    "Graph identity is shared by all structures and probes, so structure_code "
    "and probe_code are 0 (not applicable) in family, graph, and candidate seed "
    "keys.",
    "'Use the next derived seed' after a disconnected draw means attempt r uses "
    "repeat_index=r in the graph-draw key, starting at r=0.",
    "Family assignment is one seeded permutation of the family-label multiset "
    "over the stratum-ordered graph list (width, then depth, then graph index).",
    "One graph is drawn per (width, depth, graph_index); candidate parameters are "
    "drawn per (width, depth, graph_index, candidate_index).",
    "E5-prime uses the lexicographically smallest vertex triple (i<j<k) whose "
    "induced subgraph is connected.",
    "Graph generators are NumPy implementations, not a third-party library.",
)


@dataclass(frozen=True)
class GraphRecord:
    split: str
    graph_id: str
    width: int
    depth: int
    graph_index: int
    family: str
    edges: tuple[tuple[int, int], ...]
    attempts: int
    rejected_disconnected: int
    first_edge: tuple[int, int]
    first_connected_triple: tuple[int, int, int]
    candidates: tuple[dict[str, list[float]], ...] = field(default_factory=tuple)


def rng_for(split: str, artifact_code: int, **fields: int) -> np.random.Generator:
    key = contract.seed_key(
        split=split,
        artifact_code=artifact_code,
        structure_code=fields.get("structure_code", NOT_APPLICABLE),
        probe_code=fields.get("probe_code", NOT_APPLICABLE),
        width=fields.get("width", 0),
        depth=fields.get("depth", 0),
        graph_index=fields.get("graph_index", 0),
        candidate_index=fields.get("candidate_index", 0),
        repeat_index=fields.get("repeat_index", 0),
        parameter_index=fields.get("parameter_index", 0),
        allow_holdout=True,  # access control is enforced by split_guard
    )
    return np.random.default_rng(np.random.SeedSequence(list(key)))


def is_connected(width: int, edges: Sequence[tuple[int, int]]) -> bool:
    adjacency: dict[int, set[int]] = {node: set() for node in range(width)}
    for i, j in edges:
        adjacency[i].add(j)
        adjacency[j].add(i)
    seen = {0}
    stack = [0]
    while stack:
        node = stack.pop()
        for neighbour in adjacency[node]:
            if neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    return len(seen) == width


def _normalise(edges: set[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((min(i, j), max(i, j)) for i, j in edges))


def erdos_renyi(width: int, rng: np.random.Generator) -> tuple[tuple[int, int], ...]:
    pairs = list(itertools.combinations(range(width), 2))
    keep = rng.random(len(pairs)) < 0.5
    return tuple(pair for pair, flag in zip(pairs, keep, strict=True) if flag)


def watts_strogatz(width: int, rng: np.random.Generator) -> tuple[tuple[int, int], ...]:
    k = 2 if width == 4 else 4
    p = 0.30
    edges: set[tuple[int, int]] = set()
    for step in range(1, k // 2 + 1):
        for node in range(width):
            edges.add(tuple(sorted((node, (node + step) % width))))
    for step in range(1, k // 2 + 1):
        for node in range(width):
            edge = tuple(sorted((node, (node + step) % width)))
            if edge not in edges or rng.random() >= p:
                continue
            neighbours = {b if a == node else a for a, b in edges if node in (a, b)}
            choices = [w for w in range(width) if w != node and w not in neighbours]
            if not choices:
                continue
            new = choices[int(rng.integers(len(choices)))]
            edges.remove(edge)
            edges.add(tuple(sorted((node, new))))
    return _normalise(edges)


def barabasi_albert(
    width: int, rng: np.random.Generator
) -> tuple[tuple[int, int], ...]:
    m = 2
    edges: set[tuple[int, int]] = {(0, node) for node in range(1, m + 1)}
    repeated: list[int] = []
    for a, b in sorted(edges):
        repeated.extend((a, b))
    for source in range(m + 1, width):
        targets: set[int] = set()
        while len(targets) < m:
            targets.add(repeated[int(rng.integers(len(repeated)))])
        for target in sorted(targets):
            edges.add((target, source))
            repeated.extend((target, source))
    return _normalise(edges)


GENERATORS = {
    "erdos_renyi": erdos_renyi,
    "watts_strogatz": watts_strogatz,
    "barabasi_albert": barabasi_albert,
}


def draw_graph(
    split: str, family: str, width: int, depth: int, graph_index: int
) -> tuple[tuple[tuple[int, int], ...], int]:
    for attempt in range(MAX_GRAPH_ATTEMPTS):
        rng = rng_for(
            split,
            ARTIFACT_GRAPH,
            width=width,
            depth=depth,
            graph_index=graph_index,
            repeat_index=attempt,
        )
        edges = GENERATORS[family](width, rng)
        if edges and is_connected(width, edges):
            return edges, attempt + 1
    raise RuntimeError(
        f"no connected {family} graph after {MAX_GRAPH_ATTEMPTS} attempts "
        f"(split={split}, width={width}, depth={depth}, index={graph_index})"
    )


def first_connected_triple(
    width: int, edges: Sequence[tuple[int, int]]
) -> tuple[int, int, int]:
    edge_set = set(edges)
    for triple in itertools.combinations(range(width), 3):
        induced = [
            pair for pair in itertools.combinations(triple, 2) if pair in edge_set
        ]
        if len(induced) >= 2:
            return triple
    raise ValueError("graph has no connected vertex triple")


def assign_families(split: str) -> list[str]:
    totals = FAMILY_TOTALS[split]
    labels = [family for family in FAMILIES for _ in range(totals[family])]
    expected = GRAPHS_PER_STRATUM[split] * len(contract.WIDTHS) * len(contract.DEPTHS)
    if len(labels) != expected:
        raise AssertionError(f"family totals {len(labels)} != graph count {expected}")
    rng = rng_for(split, ARTIFACT_FAMILY)
    order = rng.permutation(len(labels))
    return [labels[index] for index in order]


def draw_candidates(
    split: str, width: int, depth: int, graph_index: int
) -> tuple[dict[str, list[float]], ...]:
    candidates = []
    for candidate in range(CANDIDATES):
        rng = rng_for(
            split,
            ARTIFACT_CANDIDATE,
            width=width,
            depth=depth,
            graph_index=graph_index,
            candidate_index=candidate,
        )
        gammas = rng.uniform(0.0, 2.0 * math.pi, size=depth)
        betas = rng.uniform(0.0, math.pi, size=depth)
        candidates.append(
            {
                "gamma": [float(value) for value in gammas],
                "beta": [float(value) for value in betas],
                "identity_pairs": candidate == 1,
            }
        )
    return tuple(candidates)


def build_manifest(split: str, repo: Path) -> list[GraphRecord]:
    """Build a manifest after ``split_guard`` admits the split."""

    split_guard.require_split(repo, split)
    families = iter(assign_families(split))
    records: list[GraphRecord] = []
    for width in contract.WIDTHS:
        for depth in contract.DEPTHS:
            for graph_index in range(GRAPHS_PER_STRATUM[split]):
                family = next(families)
                edges, attempts = draw_graph(split, family, width, depth, graph_index)
                records.append(
                    GraphRecord(
                        split=split,
                        graph_id=f"{split}-w{width}-p{depth}-g{graph_index}",
                        width=width,
                        depth=depth,
                        graph_index=graph_index,
                        family=family,
                        edges=edges,
                        attempts=attempts,
                        rejected_disconnected=attempts - 1,
                        first_edge=edges[0],
                        first_connected_triple=first_connected_triple(width, edges),
                        candidates=draw_candidates(split, width, depth, graph_index),
                    )
                )
    return records


def manifest_json(records: Sequence[GraphRecord]) -> str:
    payload = {
        "root_seed": contract.ROOT_SEED,
        "numpy_version": np.__version__,
        "implementation_notes": list(IMPLEMENTATION_NOTES),
        "graphs": [asdict(record) for record in records],
    }
    return json.dumps(payload, indent=1, sort_keys=True) + "\n"


def manifest_sha256(records: Sequence[GraphRecord]) -> str:
    """Hash of the graph and candidate content only.

    Environment metadata such as the NumPy version is excluded, so the same
    logical manifest hashes identically on every platform.
    """

    content = json.dumps([asdict(record) for record in records], sort_keys=True)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", required=True, choices=sorted(GRAPHS_PER_STRATUM))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if args.output.exists():
        print(f"Refusing to overwrite existing manifest: {args.output}")
        return 1
    records = build_manifest(args.split, repo)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(manifest_json(records))
    print(f"graphs={len(records)} sha256={manifest_sha256(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
