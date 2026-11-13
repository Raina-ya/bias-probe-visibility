"""Protocol v4 cell definitions: components, matched nulls, designated probes.

The authoritative labels are in ``docs/theory/06_matrix_v4.csv``; this module
holds the frozen mapping that turns a raw row into the statistic each cell
uses, and the null each cell is calibrated against.
"""

from __future__ import annotations

import csv
from pathlib import Path

BIAS_PROBES = ("P1", "P2", "P3", "P4a", "P4b", "P5")
STRUCTURES = ("E1", "E2", "E3", "E4", "E5", "E5'", "E6")

# Matched null: the structure at zero strength of its tested component.
MATCHED_NULL = {
    "E1": "0.0",
    "E2": "0.0",
    "E3": "0.0",
    "E4": "(0.0,0.0)",
    "E5": "0.0",  # keeps the 0.10 marginal pair flips
    "E5'": "0.0",  # keeps the 0.25 marginal triple flips
    "E6": "0.0",  # keeps baseline rates 0.04/0.06
}

# Component of the raw row used by each cell (default: row.statistic).
COMPONENT = {
    **{("P4a", s): "assignment" for s in ("E1", "E2", "E3", "E4", "E5", "E5'")},
    ("P4a", "E6"): "temporal_contrast",
    **{("P4b", s): "t_marg" for s in ("E1", "E2", "E3", "E4")},
    ("P4b", "E5"): "t_corr",
    ("P4b", "E5'"): "t_corr",
    ("P4b", "E6"): "temporal_contrast",
}

# Decision endpoint: one designated probe per structure, calibrated on clean E0.
DESIGNATED = {
    "E1": "P1",
    "E2": "P2",
    "E3": "P3",
    "E4": "P4a",
    "E5": "P4a",
    "E5'": "P4a",
    "E6": "P4a",
}

MATRIX = Path(__file__).resolve().parents[1] / "docs" / "theory" / "06_matrix_v4.csv"


def cells() -> list[tuple[str, str]]:
    return [(p, s) for p in BIAS_PROBES for s in STRUCTURES]


def component(probe: str, structure: str) -> str:
    return COMPONENT.get((probe, structure), "statistic")


def cell_value(row, probe: str, structure: str) -> float:
    key = component(probe, structure)
    return row.statistic if key == "statistic" else row.components[key]


def load_matrix(path: Path = MATRIX) -> dict[tuple[str, str], dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {(r["probe"], r["structure"]): r for r in csv.DictReader(handle)}
