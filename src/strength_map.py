"""Development strength map, protocol v3 Section 4.2.

For every non-null structure the main operating point uses the largest frozen
absolute strength and the sensitivity point the smallest.  Where two settings
share that magnitude (a sign, or an E4 orientation), the one with the smaller
development median of the signed harmful ratio beta/Delta is chosen; medians
within 1e-12 are tied and the tie goes to the earlier setting in the frozen
order below (negative sign first; E4 in listed order).

Input rows are development reference records ``(structure, setting, graph_id,
ratio, ideal_tie)``.  Exact ideal ties are omitted from medians only.
"""

from __future__ import annotations

import csv
import io
import statistics
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

TIE_TOLERANCE = 1e-12
POINTS = ("main", "sensitivity")


def _signed(values: Sequence[float]) -> list[tuple[str, float]]:
    ordered = sorted(
        values, key=lambda v: (abs(v), v)
    )  # negative first within a magnitude
    return [(repr(v), abs(v)) for v in ordered]


E4_SETTINGS = (
    (0.01, 0.02),
    (0.02, 0.04),
    (0.04, 0.08),
    (0.08, 0.12),
    (0.02, 0.01),
    (0.04, 0.02),
    (0.08, 0.04),
    (0.12, 0.08),
)

# structure -> frozen order of (setting label, magnitude)
GRIDS: dict[str, list[tuple[str, float]]] = {
    "E1": [(repr(p), p) for p in (0.0025, 0.005, 0.01, 0.02, 0.04)],
    "E2": _signed([s * x for x in (0.005, 0.01, 0.02, 0.04) for s in (-1, 1)]),
    "E3": _signed([s * x for x in (0.005, 0.01, 0.02, 0.04) for s in (-1, 1)]),
    "E4": [(f"({a},{b})", round(a + b, 12)) for a, b in E4_SETTINGS],
    "E5": _signed([s * x for x in (0.0025, 0.0050, 0.0075, 0.0100) for s in (-1, 1)]),
    "E5'": _signed(
        [
            s * x
            for x in (0.00390625, 0.00781250, 0.01171875, 0.01562500)
            for s in (-1, 1)
        ]
    ),
    "E6": _signed([s * x for x in (0.005, 0.010, 0.020, 0.030) for s in (-1, 1)]),
}
NON_NULL_STRUCTURES = tuple(GRIDS)
FIELDS = (
    "structure",
    "point",
    "setting",
    "magnitude",
    "development_median",
    "chosen",
    "graphs_used",
    "ties_omitted",
    "input_sha256",
)


@dataclass(frozen=True)
class ReferenceRow:
    structure: str
    setting: str
    graph_id: str
    ratio: float
    ideal_tie: bool


@dataclass(frozen=True)
class SettingSummary:
    structure: str
    point: str
    setting: str
    magnitude: float
    development_median: float
    chosen: bool
    graphs_used: int
    ties_omitted: int


def _medians(
    rows: Iterable[ReferenceRow], structure: str
) -> dict[str, tuple[float, int, int]]:
    grouped: dict[str, list[ReferenceRow]] = defaultdict(list)
    for row in rows:
        if row.structure == structure:
            grouped[row.setting].append(row)
    result = {}
    for setting, members in grouped.items():
        kept = [row.ratio for row in members if not row.ideal_tie]
        if not kept:
            raise ValueError(f"{structure} {setting}: every graph is an ideal tie")
        result[setting] = (statistics.median(kept), len(kept), len(members) - len(kept))
    return result


def choose(rows: Sequence[ReferenceRow]) -> list[SettingSummary]:
    summaries: list[SettingSummary] = []
    for structure, grid in GRIDS.items():
        medians = _medians(rows, structure)
        magnitudes = sorted({magnitude for _, magnitude in grid})
        for point, magnitude in (
            ("main", magnitudes[-1]),
            ("sensitivity", magnitudes[0]),
        ):
            candidates = [label for label, m in grid if m == magnitude]
            missing = [label for label in candidates if label not in medians]
            if missing:
                raise ValueError(
                    f"{structure} {point}: no development rows for {missing}"
                )
            best = candidates[0]
            for label in candidates[1:]:
                if medians[label][0] < medians[best][0] - TIE_TOLERANCE:
                    best = label
            for label in candidates:
                median, used, ties = medians[label]
                summaries.append(
                    SettingSummary(
                        structure,
                        point,
                        label,
                        magnitude,
                        median,
                        label == best,
                        used,
                        ties,
                    )
                )
    return summaries


def chosen_settings(summaries: Sequence[SettingSummary]) -> dict[tuple[str, str], str]:
    return {(s.structure, s.point): s.setting for s in summaries if s.chosen}


def render_csv(summaries: Sequence[SettingSummary], input_sha256: str) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    for s in summaries:
        writer.writerow(
            {
                "structure": s.structure,
                "point": s.point,
                "setting": s.setting,
                "magnitude": repr(s.magnitude),
                "development_median": repr(s.development_median),
                "chosen": int(s.chosen),
                "graphs_used": s.graphs_used,
                "ties_omitted": s.ties_omitted,
                "input_sha256": input_sha256,
            }
        )
    return buffer.getvalue()
