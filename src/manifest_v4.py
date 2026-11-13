"""Manifest entry point for protocol v4.

Identical graph and candidate construction to ``manifest.py`` (registered with
v3), but admitted by the v4 split lock.  Part 2 code must use this entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import manifest as base  # noqa: E402
import protocol_contract as contract  # noqa: E402
import split_guard_v4  # noqa: E402


def build_manifest(split: str, repo: Path) -> list[base.GraphRecord]:
    split_guard_v4.require_split(repo, split)
    families = iter(base.assign_families(split))
    records = []
    for width in contract.WIDTHS:
        for depth in contract.DEPTHS:
            for graph_index in range(base.GRAPHS_PER_STRATUM[split]):
                family = next(families)
                edges, attempts = base.draw_graph(
                    split, family, width, depth, graph_index
                )
                records.append(
                    base.GraphRecord(
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
                        first_connected_triple=base.first_connected_triple(
                            width, edges
                        ),
                        candidates=base.draw_candidates(
                            split, width, depth, graph_index
                        ),
                    )
                )
    return records
