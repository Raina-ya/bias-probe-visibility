"""Offline dry run of the whole hardware package (split 99; never a result).

Runs preflight, pilot, allocate, main and the analysis through the same code
as the real run, with a FakeAdapter instead of IBM: a fixed synthetic device
(Qiskit GenericBackendV2 topology, readout errors drawn once from split 99),
synthetic counts from a known readout model, and a linear model of reported
QPU seconds.  No account, network or QPU is used.

Scenarios:
  null        independent flips at each selected qubit's reported error
  correlated  as null, plus covariance 1.5 c* on logical pair (0, 1) in both
              preparations; the relevance test should reject that pair

The clock is fixed so outputs are reproducible under the pinned NumPy
(2.3.4; CI and the reference workstation).  Outputs go to
experiments/hardware/dry_run/ and must not exist beforehand.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hw_analysis_v1 as ha  # noqa: E402
import hw_circuits_v1 as hc  # noqa: E402
import hw_rawio_v1 as rio  # noqa: E402
import hw_runner_v1 as hr  # noqa: E402
import hw_stats_v1 as st  # noqa: E402

OUTPUTS = ("dry_run_v1_summary.json", "dry_run_v1_log.txt")
ROOT_SEED = 20261111
SPLIT = 99
FIXED_CLOCK = "2026-01-01T00:00:00.000000Z"
FAKE_DATE = "2026-01-01"
FAKE_BACKEND = "fake_generic_27"
USAGE_FIXED = 2.0      # seconds per job (synthetic)
USAGE_PER_SHOT = 2.5e-4  # seconds per shot (synthetic)
MAX_SHOTS = 50000
SCENARIOS = ("null", "correlated")


def fixed_clock() -> str:
    return FIXED_CLOCK


def fake_errors(num_qubits: int) -> dict[int, float]:
    rng = np.random.default_rng(np.random.SeedSequence([ROOT_SEED, SPLIT, 5, 5, 40, 0, 0, 0, 0, 0, 0]))
    return {q: float(round(x, 6)) for q, x in enumerate(rng.uniform(0.006, 0.04, num_qubits))}


class FakeAdapter:
    """Synthetic device with the IBMAdapter interface (dry runs and tests)."""

    def __init__(self, scenario: str, num_qubits: int = 27, usage_fixed: float = USAGE_FIXED,
                 usage_per_shot: float = USAGE_PER_SHOT, fail_job: int | None = None,
                 main_slowdown: float = 1.0):
        from qiskit.providers.fake_provider import GenericBackendV2

        self.backend = GenericBackendV2(num_qubits=num_qubits, seed=SPLIT)
        self.name = FAKE_BACKEND
        self.scenario = scenario
        self.errors = fake_errors(num_qubits)
        self.usage_fixed, self.usage_per_shot = usage_fixed, usage_per_shot
        self.fail_job = fail_job
        self.main_slowdown = main_slowdown  # tests: main jobs slower than the pilot predicts
        self._jobs: dict[str, dict] = {}
        self._physical: list[int] | None = None
        self.submitted = 0

    def readout_errors(self):
        return dict(self.errors)

    def edges(self):
        return [tuple(e) for e in self.backend.coupling_map.get_edges()]

    def calibration_timestamp(self):
        return FIXED_CLOCK

    def transpile(self, circuits, physical):
        from qiskit import transpile

        self._physical = list(physical)
        return transpile(circuits, self.backend, initial_layout=physical,
                         optimization_level=0, seed_transpiler=hc.TRANSPILE_SEED)

    def dump(self, circuit):
        from qiskit import qasm3

        return qasm3.dumps(circuit)

    def options_record(self):
        return {"class": "FakeAdapter", "twirling_enable_gates": False,
                "twirling_enable_measure": False, "dynamical_decoupling_enable": False}

    def _distribution(self, circuit: str) -> dict[str, float]:
        """Probabilities of internal outcome strings for one circuit."""

        q = [self.errors[p] for p in self._physical]
        probs = {}
        for flips in np.ndindex(*([2] * hc.WIDTH)):
            w = 1.0
            start = 0
            if self.scenario == "correlated":
                c = 1.5 * st.c_star(q[0], q[1])
                w = st.joint(q[0], q[1], c)[2 * flips[0] + flips[1]]
                start = 2
            for k in range(start, hc.WIDTH):
                w *= q[k] if flips[k] else 1 - q[k]
            prepared = hc.PREPARED_BIT[circuit]
            z = "".join(str(prepared ^ f) for f in flips)
            probs[z] = probs.get(z, 0.0) + w
        return probs

    def submit(self, circuits, shots, max_seconds):
        index = self.submitted
        self.submitted += 1
        job_id = f"dryrun-{self.scenario}-{index}"
        counts = []
        for ci, (c, n) in enumerate(zip(circuits, shots, strict=True)):
            dist = self._distribution(c.name)
            keys = sorted(dist)
            p = np.array([dist[k] for k in keys])
            rng = np.random.default_rng(np.random.SeedSequence(
                [ROOT_SEED, SPLIT, 6, 5, 40, hc.WIDTH, 0, index, ci, 0, SCENARIOS.index(self.scenario)]))
            draw = rng.multinomial(int(n), p / p.sum())
            counts.append({k[::-1]: int(m) for k, m in zip(keys, draw, strict=True) if m})
        usage = self.usage_fixed + self.usage_per_shot * sum(shots)
        if index > 0:
            usage *= self.main_slowdown
        status = "FAILED" if index == self.fail_job else "DONE"
        if usage > max_seconds:
            status = "CANCELLED_MAX_EXECUTION_TIME"
        self._jobs[job_id] = {"status": status, "counts": counts if status == "DONE" else None,
                              "usage_seconds": usage if status == "DONE" else None,
                              "metrics": {"usage": {"synthetic_seconds": usage}}}
        return job_id

    def fetch(self, job_id):
        return dict(self._jobs[job_id])


def inputs() -> dict:
    return {
        "authorization_v1": {"backend": FAKE_BACKEND, "run_date": FAKE_DATE,
                             "statement": hr.STATEMENT, "signed_by": "DRY RUN (no owner signature)",
                             "signed_date": FAKE_DATE},
        "terms_check_v1": {"checked_date": FAKE_DATE, "sources": ["dry run: no terms read"],
                           "allowance": "synthetic", "unit_conversion": "synthetic",
                           "max_shots_per_circuit": MAX_SHOTS, "allows_run": True},
    }


def run_scenario(repo: Path, out_root: Path, scenario: str, boot: int = ha.BOOT) -> dict:
    run_dir = out_root / scenario
    ctx = hr.Context(repo=repo, out=run_dir, adapter=FakeAdapter(scenario), real=False,
                     today=FAKE_DATE, clock=fixed_clock, inputs=inputs())
    pre = hr.preflight(ctx)
    hr.pilot(ctx)
    alloc = hr.allocate(ctx)
    hr.main_stage(ctx)
    result = ha.run(run_dir, out_root / f"{scenario}_analysis", dry_run=True, boot=boot)
    flagged = [r["pair"] + [r["circuit"]] for r in result["pairs"] if r["relevance_reject"]]
    index = {e["file"]: e["sha256"] for e in rio.read_lines(run_dir / rio.INDEX)}
    return {
        "selected_physical_qubits": pre["selected_physical_qubits"],
        "median_readout_error": pre["median_readout_error"],
        "allocation": {k: alloc[k] for k in ("go", "reason", "r", "s_remaining", "q_run",
                                             "s_min", "margin_shots") if k in alloc},
        "main_jobs": len(alloc.get("plan", [])),
        "shots_per_circuit": result["shots_per_circuit"],
        "H_R1": result["H_R1"],
        "relevance_rejections": result["relevance_rejections"],
        "relevance_rejected_pairs": flagged,
        "detection_rejections": result["detection_rejections"],
        "max_c_upper_95": result["max_c_upper_95"],
        "record_sha256": index,
        "analysis_sha256": rio.canonical_sha256(out_root / f"{scenario}_analysis" / ha.OUTPUTS[0]),
        "index_problems": rio.verify_index(run_dir),
    }


def run(repo: Path, out_root: Path, boot: int = ha.BOOT) -> dict:
    if out_root.exists():
        raise SystemExit(f"{out_root} exists; dry-run outputs are written once")
    summary = {"split": SPLIT, "purpose": "offline dry run; never a result",
               "numpy": np.__version__, "bootstrap": boot,
               "scenarios": {s: run_scenario(repo, out_root, s, boot) for s in SCENARIOS}}
    return summary


def cli(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=hr.REPO / "experiments" / "hardware" / "dry_run")
    ap.add_argument("--boot", type=int, default=ha.BOOT)
    args = ap.parse_args(argv)
    summary = run(hr.REPO, args.out, args.boot)
    text = json.dumps(summary, indent=1, sort_keys=True) + "\n"
    (args.out / OUTPUTS[0]).write_text(text, encoding="utf-8", newline="\n")
    log = [f"{s}: {v['H_R1']}; relevance rejections {v['relevance_rejections']} "
           f"{v['relevance_rejected_pairs']}; detection {v['detection_rejections']}; "
           f"allocation go={v['allocation']['go']} ({v['allocation']['reason']}); "
           f"main jobs {v['main_jobs']}; shots {v['shots_per_circuit']}; "
           f"index problems {v['index_problems']}"
           for s, v in summary["scenarios"].items()]
    (args.out / OUTPUTS[1]).write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())

