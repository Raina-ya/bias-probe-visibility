"""Execution contract for protocol v3 Part 2 (Sections 6, 7, 9).

One call to ``run_row`` produces one immutable aggregate raw row for one
graph / probe / structure / setting / repeat.  It builds the probe's frozen
circuit list, allocates exactly ``N=16,384`` shots, applies the E6 block
schedule when needed, draws multinomial counts from exact probabilities, and
computes the probe statistic from counts only.  Ideal target values are never
computed here; ``reference.py`` computes them separately for the strength map
and scoring.
"""

from __future__ import annotations

import math
import time
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

import channels
import circuits
import probes
import protocol_contract as contract
import simulate

N = contract.TOTAL_SHOTS
MAIN_FRACTION = 0.10
STRUCTURE_CODES = {
    "E0": 0,
    "E1": 1,
    "E2": 2,
    "E3": 3,
    "E4": 4,
    "E5": 5,
    "E5'": 55,
    "E6": 6,
    "E7": 7,
}
PROBE_CODES = {
    "P0": 0,
    "P1": 1,
    "P2": 2,
    "P3": 3,
    "P4a": 40,
    "P4b": 41,
    "P1b": 11,
    "P5": 50,
    "GVS": 90,
}
ARTIFACT_COMPILE = 4
ARTIFACT_SHOTS = 6
ZERO_EXTRA = frozenset({"P0", "P5"})
BLOCKS = 8


@dataclass(frozen=True)
class Entry:
    """One measured circuit in canonical order."""

    label: str
    role: str  # "target" or "probe"
    candidate: int | None
    circuit: circuits.Compiled


@dataclass
class Row:
    split: str
    graph_id: str
    width: int
    depth: int
    graph_index: int
    family: str
    probe: str
    structure: str
    setting: str
    parameter_index: int
    repeat: int
    fraction: float
    seed_key: tuple[int, ...]
    target_shots: int
    probe_shots: int
    circuits: list[dict] = field(default_factory=list)
    statistic: float = math.nan
    components: dict = field(default_factory=dict)
    alarm_p0: bool | None = None
    unique_solves: int = 0
    elapsed_seconds: float = 0.0
    depth_multiplier: float = 1.0
    commit: str = ""
    protocol_sha256: str = ""

    @property
    def total_shots(self) -> int:
        return self.target_shots + self.probe_shots


def _key(split, artifact, structure, probe, record, candidate, repeat, parameter):
    return contract.seed_key(
        split=split,
        artifact_code=artifact,
        structure_code=STRUCTURE_CODES[structure],
        probe_code=PROBE_CODES[probe],
        width=record.width,
        depth=record.depth,
        graph_index=record.graph_index,
        candidate_index=candidate,
        repeat_index=repeat,
        parameter_index=parameter,
        allow_holdout=True,  # access control is split_guard's job
    )


def transpiler_seed(split: str, record, candidate: int) -> int:
    key = _key(split, ARTIFACT_COMPILE, "E0", "P0", record, candidate, 0, 0)
    return int(np.random.SeedSequence(list(key)).generate_state(1)[0])


# ---------------------------------------------------------------- circuits


def target_circuits(
    split: str, record, condition: channels.Condition
) -> list[circuits.Compiled]:
    out = []
    for index, candidate in enumerate(record.candidates):
        compiled = circuits.compile_target(
            record.width,
            record.edges,
            candidate,
            transpiler_seed(split, record, index),
            epsilon=condition.epsilon,
        )
        if candidate["identity_pairs"]:
            circuits.assert_identity_pairs(compiled, record.edges[0], record.depth)
        out.append(compiled)
    return out


def entries_for(probe: str, split: str, record, condition) -> list[Entry]:
    targets = target_circuits(split, record, condition)
    out = [Entry(f"target{c}", "target", c, t) for c, t in enumerate(targets)]
    w = record.width
    if probe in ("P0", "P5"):
        return out
    if probe in ("P1", "P1b"):
        out += [
            Entry(f"fold3_{c}", "probe", c, circuits.fold(t, 3))
            for c, t in enumerate(targets)
        ]
    elif probe == "P2":
        out += [
            Entry(f"twin{c}", "probe", c, circuits.clifford_twin(t))
            for c, t in enumerate(targets)
        ]
    elif probe == "P3":
        rows = circuits.frame_rows(w)
        for c, t in enumerate(targets):
            out += [
                Entry(f"frame{c}_{h}", "probe", c, circuits.framed(t, rows[h]))
                for h in range(16)
            ]
    elif probe == "P4a":
        out += [
            Entry("prep0", "probe", None, circuits.preparation(w, {}, "prep0")),
            Entry(
                "prep1",
                "probe",
                None,
                circuits.preparation(w, {q: 1 for q in range(w)}, "prep1"),
            ),
        ]
    elif probe == "P4b":
        for i in range(w):
            for j in range(i + 1, w):
                for a in (0, 1):
                    for b in (0, 1):
                        name = f"pair{i}{j}_prep{a}{b}"
                        out.append(
                            Entry(
                                name,
                                "probe",
                                None,
                                circuits.preparation(w, {i: a, j: b}, name),
                            )
                        )
    else:
        raise ValueError(f"unsupported probe {probe}")
    return out


# ---------------------------------------------------------------- allocation


def allocate(probe: str, entries: Sequence[Entry], fraction: float) -> dict[str, int]:
    probe_labels = [e.label for e in entries if e.role == "probe"]
    target_labels = [e.label for e in entries if e.role == "target"]
    n_probe = 0 if probe in ZERO_EXTRA or not probe_labels else math.floor(fraction * N)
    shots = contract.split_even(N - n_probe, target_labels)
    if probe_labels:
        shots.update(contract.split_even(n_probe, probe_labels))
    if sum(shots.values()) != N:
        raise AssertionError("allocation does not conserve the fixed budget")
    return shots


def _split_blocks(total: int, blocks: Sequence[int]) -> dict[int, int]:
    quotient, remainder = divmod(total, len(blocks))
    return {b: quotient + (k < remainder) for k, b in enumerate(blocks)}


def e6_schedule(probe, entries, shots, permutation_rng) -> list[tuple[str, int, int]]:
    """Return ``(label, block, shots)`` triples, Section 7."""

    out: list[tuple[str, int, int]] = []
    if probe in ("P4a", "P4b"):
        for e in entries:
            blocks = (1, 2, 3, 4, 5, 6) if e.role == "target" else (0, 7)
            for b, n in _split_blocks(shots[e.label], blocks).items():
                out.append((e.label, b, n))
    elif probe in ("P0", "P5"):
        for e in entries:
            for b, n in _split_blocks(shots[e.label], tuple(range(BLOCKS))).items():
                out.append((e.label, b, n))
    else:
        order = [entries[k].label for k in permutation_rng.permutation(len(entries))]
        halves = {lab: (math.ceil(shots[lab] / 2), shots[lab] // 2) for lab in order}
        for half, sequence, first_block in ((0, order, 0), (1, order[::-1], 4)):
            total = sum(halves[lab][half] for lab in sequence)
            sizes = _split_blocks(total, (0, 1, 2, 3))
            boundaries = np.cumsum([0] + [sizes[k] for k in range(4)])
            start = 0
            for lab in sequence:
                n = halves[lab][half]
                for k in range(4):
                    overlap = max(
                        0, min(start + n, boundaries[k + 1]) - max(start, boundaries[k])
                    )
                    if overlap:
                        out.append((lab, first_block + k, int(overlap)))
                start += n
    if sum(n for _, _, n in out) != N:
        raise AssertionError("E6 schedule does not conserve the fixed budget")
    return out


def block_time(block: int) -> float:
    return (2 * block + 1) / 16


# ---------------------------------------------------------------- execution


class SolveCache:
    def __init__(self) -> None:
        self._cache: dict[tuple, np.ndarray] = {}

    def get(self, circuit: circuits.Compiled, noise: simulate.GateNoise) -> np.ndarray:
        key = (circuit.sha256(), noise)
        if key not in self._cache:
            self._cache[key] = simulate.probabilities(circuit, noise)
        return self._cache[key]

    def __len__(self) -> int:
        return len(self._cache)


def _counts(rng, probabilities: np.ndarray, shots: int, width: int) -> dict[str, int]:
    drawn = rng.multinomial(shots, probabilities)
    return {format(k, f"0{width}b"): int(n) for k, n in enumerate(drawn) if n}


def _merge(parts: Sequence[dict[str, int]]) -> dict[str, int]:
    merged: dict[str, int] = {}
    for part in parts:
        for z, n in part.items():
            merged[z] = merged.get(z, 0) + n
    return merged


def run_row(
    *,
    split: str,
    record,
    probe: str,
    structure: str,
    setting: str,
    parameter_index: int,
    repeat: int,
    fraction: float = MAIN_FRACTION,
    cache: SolveCache | None = None,
    commit: str = "",
    protocol_sha256: str = "",
) -> Row:
    started = time.perf_counter()
    cache = cache if cache is not None else SolveCache()
    before = len(cache)
    condition = channels.parse_condition(structure, setting)
    entries = entries_for(probe, split, record, condition)
    shots = allocate(probe, entries, fraction)
    key = _key(
        split, ARTIFACT_SHOTS, structure, probe, record, 0, repeat, parameter_index
    )
    root = np.random.SeedSequence(list(key))
    w = record.width

    if structure == "E6":
        perm_key = _key(
            split, ARTIFACT_COMPILE, "E6", probe, record, 0, repeat, parameter_index
        )
        schedule = e6_schedule(
            probe,
            entries,
            shots,
            np.random.default_rng(np.random.SeedSequence(list(perm_key))),
        )
    else:
        schedule = [(e.label, -1, shots[e.label]) for e in entries]

    by_label = {e.label: e for e in entries}
    children = root.spawn(len(schedule))
    measured: dict[str, list[dict[str, int]]] = {e.label: [] for e in entries}
    by_block: dict[str, dict[int, dict[str, int]]] = {e.label: {} for e in entries}
    ledger = []
    for (label, block, n), child in zip(schedule, children, strict=True):
        entry = by_label[label]
        pre = cache.get(entry.circuit, condition.gate)
        readout = channels.readout_for(
            condition,
            w,
            record.first_edge,
            record.first_connected_triple,
            block_time(block) if block >= 0 else None,
        )
        post = channels.apply_readout(pre, w, readout)
        counts = _counts(np.random.default_rng(child), post, n, w) if n else {}
        measured[label].append(counts)
        by_block[label][block] = counts
        ledger.append(
            {
                "label": label,
                "role": entry.role,
                "block": block,
                "shots": n,
                "circuit_sha256": entry.circuit.sha256(),
                "counts": counts,
            }
        )
    pooled = {label: _merge(parts) for label, parts in measured.items()}

    row = Row(
        split=split,
        graph_id=record.graph_id,
        width=w,
        depth=record.depth,
        graph_index=record.graph_index,
        family=record.family,
        probe=probe,
        structure=structure,
        setting=setting,
        parameter_index=parameter_index,
        repeat=repeat,
        fraction=0.0 if probe in ZERO_EXTRA else fraction,
        seed_key=key,
        target_shots=sum(shots[e.label] for e in entries if e.role == "target"),
        probe_shots=sum(shots[e.label] for e in entries if e.role == "probe"),
        circuits=ledger,
        commit=commit,
        protocol_sha256=protocol_sha256,
    )
    if row.total_shots != N:
        raise AssertionError("row does not charge exactly the fixed budget")

    edges = record.edges
    targets = [pooled["target0"], pooled["target1"]]
    row.components["gap_target"] = probes.gap(
        targets[0], targets[1], edges, condition.offset
    )
    row.alarm_p0 = (
        probes.p0_lower_bound(targets[0], targets[1], edges, condition.offset) <= 0
    )
    if probe == "P0":
        row.statistic = probes.p0_lower_bound(
            targets[0], targets[1], edges, condition.offset
        )
    elif probe in ("P1", "P1b"):
        folded = [pooled["fold3_0"], pooled["fold3_1"]]
        row.statistic = probes.p1_score(targets, folded, edges)
        row.components["p1b_w_neg"] = probes.p1b_score(targets, folded)
        row.depth_multiplier = 3.0
        if probe == "P1b":
            row.statistic = row.components["p1b_w_neg"]
    elif probe == "P2":
        twins = [by_label["twin0"].circuit, by_label["twin1"].circuit]
        scores = simulate.cut_scores(w, edges)
        clean = simulate.GateNoise()
        reference = float(
            cache.get(twins[0], clean) @ scores - cache.get(twins[1], clean) @ scores
        )
        row.components["twin_reference_gap"] = reference
        row.statistic = probes.p2_score(
            [pooled["twin0"], pooled["twin1"]], edges, reference
        )
    elif probe == "P3":
        row.statistic = probes.p3_score(
            targets,
            [pooled[f"frame0_{h}"] for h in range(16)],
            [pooled[f"frame1_{h}"] for h in range(16)],
            edges,
        )
    elif probe == "P4a":
        row.statistic = probes.p4a_score(pooled["prep0"], pooled["prep1"], w)
    elif probe == "P4b":
        pair_preps = {}
        for i in range(w):
            for j in range(i + 1, w):
                pair_preps[(i, j)] = {
                    (a, b): pooled[f"pair{i}{j}_prep{a}{b}"]
                    for a in (0, 1)
                    for b in (0, 1)
                }
        row.statistic = probes.p4b_score(pair_preps)
    elif probe == "P5":
        halves = None
        if structure == "E6":
            halves = [
                (
                    _merge([by_block[f"target{c}"][b] for b in range(4)]),
                    _merge([by_block[f"target{c}"][b] for b in range(4, 8)]),
                )
                for c in (0, 1)
            ]
        row.statistic = probes.p5_score(targets, halves)
    row.unique_solves = len(cache) - before
    row.elapsed_seconds = time.perf_counter() - started
    return row
