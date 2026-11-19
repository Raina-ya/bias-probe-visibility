"""Pilot, allocation and main runner for the hardware readout amendment v1.

Stages run in order, each from its own command, each at most once:

    preflight  check inputs, select qubits, transpile, record the run manifest
    pilot      2 P4a circuits x 1,000 shots, one job; measure reported QPU seconds
    allocate   protocol v4 Section 14 formula and the amendment's go rule
    main       the planned jobs, each with max_execution_time <= seconds left of 360

Real mode (``--real``) writes only to results/hardware_v1/ and refuses unless:
the owner's authorization (docs/hardware/authorization_v1.json) names this
backend and today's date with the exact statement; the terms check
(docs/hardware/terms_check_v1.json) is dated today and allows the run; the OSF
registration record (docs/hardware/registration_hw_v1.json) names a commit
that is an ancestor of HEAD and the SHA-256 of docs/hardware/package_manifest_v1.json;
and every file listed in that manifest still has its registered hash.

Immutability: every record is written once (hw_rawio_v1).  A stage writes an
attempt marker first and a success marker last.  A second run of a successful
stage is refused.  An interrupted stage may only resume the frozen plan: a job
whose ID was recorded is fetched by ID and never resubmitted; a planned job
never submitted may be submitted.  A failed job stops the run; going on needs a
documented owner decision outside this runner.

No credential is read, requested or written here.  The IBM adapter uses the
account already saved on the owner's machine by QiskitRuntimeService.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import platform
import statistics
import subprocess
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hw_circuits_v1 as hc  # noqa: E402
import hw_rawio_v1 as rio  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CAP_SECONDS = 360
RESERVE_SECONDS = 30
SAFETY = 1.25
PILOT_SHOTS = 1000
MAX_EXECUTION_TIME_LIMIT = 10800  # provider maximum (sampler options guide)
Q_GRID = (0.005, 0.01, 0.02, 0.05)
S_MIN = {0.005: 30000, 0.01: 10000, 0.02: 10000, 0.05: 3000}
REAL_OUT = Path("results/hardware_v1")
AUTH = Path("docs/hardware/authorization_v1.json")
TERMS = Path("docs/hardware/terms_check_v1.json")
REGISTRATION = Path("docs/hardware/registration_hw_v1.json")
MANIFEST = Path("docs/hardware/package_manifest_v1.json")
STATEMENT = (
    "I authorize one run under hardware readout amendment v1, "
    "using at most 360 reported QPU seconds."
)
STAGES = ("preflight", "pilot", "allocate", "main")


class Refused(RuntimeError):
    """A precondition failed; nothing was submitted."""


# --------------------------------------------------------------------------- inputs


def check_authorization(auth: dict, backend: str, today: str) -> None:
    for key in ("backend", "run_date", "statement", "signed_by", "signed_date"):
        if not auth.get(key):
            raise Refused(f"authorization lacks {key}")
    if auth["statement"] != STATEMENT:
        raise Refused("authorization statement differs from the frozen text")
    if auth["backend"] != backend:
        raise Refused(f"authorization names {auth['backend']}, not {backend}")
    if auth["run_date"] != today:
        raise Refused(f"authorization is for {auth['run_date']}, today is {today}")


def check_terms(terms: dict, today: str) -> None:
    for key in ("checked_date", "sources", "allowance", "unit_conversion",
                "max_shots_per_circuit", "allows_run"):
        if terms.get(key) in (None, "", []):
            raise Refused(f"terms check lacks {key}")
    if terms["checked_date"] != today:
        raise Refused("terms check is not dated today")
    if terms["allows_run"] is not True:
        raise Refused("terms check does not allow the run")
    if not isinstance(terms["max_shots_per_circuit"], int) or terms["max_shots_per_circuit"] < 1:
        raise Refused("max_shots_per_circuit must be a positive integer")


def check_registration(reg: dict, repo: Path) -> None:
    for key in ("registry", "url", "timestamp_utc", "commit", "package_manifest_sha256"):
        if not reg.get(key):
            raise Refused(f"registration lacks {key}")
    if reg["registry"] != "OSF" or not str(reg["url"]).startswith("https://osf.io/"):
        raise Refused("registration must be an OSF record")
    manifest = repo / MANIFEST
    if not manifest.is_file():
        raise Refused("package manifest missing")
    if rio.canonical_sha256(manifest) != reg["package_manifest_sha256"]:
        raise Refused("package manifest differs from the registered hash")
    listed = json.loads(manifest.read_text(encoding="utf-8"))["files"]
    for rel, digest in listed.items():
        path = repo / rel
        if not path.is_file() or rio.canonical_sha256(path) != digest:
            raise Refused(f"package file changed since registration: {rel}")
    try:
        done = subprocess.run(
            ["git", "merge-base", "--is-ancestor", reg["commit"], "HEAD"],
            cwd=repo, capture_output=True, check=False,
        )
    except OSError as exc:  # git missing
        raise Refused(f"cannot run git: {exc}") from exc
    if done.returncode != 0:
        raise Refused("registered commit is not an ancestor of HEAD")


def environment() -> dict:
    versions = {"python": sys.version.split()[0], "numpy": np.__version__}
    for mod in ("scipy", "qiskit", "qiskit_ibm_runtime", "qiskit_aer"):
        try:
            versions[mod] = __import__(mod).__version__
        except ImportError:
            versions[mod] = None
    buf = io.StringIO()
    try:
        config = np.show_config(mode="dicts")
    except TypeError:  # older numpy prints only
        with redirect_stdout(buf):
            np.show_config()
        config = buf.getvalue()
    return {"versions": versions, "platform": platform.platform(), "numpy_config": config}


def git_head(repo: Path) -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo,
                             capture_output=True, text=True, check=False)
    except OSError:
        return None
    return out.stdout.strip() or None


# --------------------------------------------------------------------------- context


@dataclass
class Context:
    repo: Path
    out: Path
    adapter: object
    real: bool
    today: str
    clock: object = rio.utc_now
    inputs: dict = field(default_factory=dict)  # dry run: authorization/terms dicts

    def marker(self, stage: str, kind: str) -> Path:
        return self.out / "markers" / f"{stage}.{kind}"

    def has(self, stage: str, kind: str = "success") -> bool:
        return self.marker(stage, kind).is_file()

    def mark(self, stage: str, kind: str, payload: dict) -> None:
        path = self.marker(stage, kind)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="\n") as h:
            h.write(json.dumps(payload, sort_keys=True) + "\n")

    def load(self, rel: Path) -> dict:
        if self.real:
            path = self.repo / rel
            if not path.is_file():
                raise Refused(f"missing {rel}")
            return json.loads(path.read_text(encoding="utf-8"))
        return self.inputs[rel.stem]


def begin(ctx: Context, stage: str, needs: str | None) -> bool:
    """Return True for a fresh stage, False when resuming an interrupted one."""

    if ctx.has(stage):
        raise Refused(f"{stage} already succeeded; a second run is refused")
    if needs and not ctx.has(needs):
        raise Refused(f"{stage} needs {needs} to have succeeded")
    if ctx.has(stage, "attempt"):
        return False
    ctx.mark(stage, "attempt", {"started_utc": ctx.clock()})
    return True


# --------------------------------------------------------------------------- stages


def preflight(ctx: Context) -> dict:
    if ctx.real and ctx.out.resolve() != (ctx.repo / REAL_OUT).resolve():
        raise Refused(f"real runs write only to {REAL_OUT}")
    if not ctx.real and ctx.out.resolve() == (ctx.repo / REAL_OUT).resolve():
        raise Refused("dry runs never write to the real output folder")
    a = ctx.adapter
    # All input checks run before any marker is written, so a wrong date or a
    # changed file can be corrected and preflight retried.
    if ctx.has("preflight"):
        raise Refused("preflight already succeeded; a second run is refused")
    check_authorization(ctx.load(AUTH), a.name, ctx.today)
    terms = ctx.load(TERMS)
    check_terms(terms, ctx.today)
    reg = None
    if ctx.real:
        reg = ctx.load(REGISTRATION)
        check_registration(reg, ctx.repo)
    begin(ctx, "preflight", None)
    errors = a.readout_errors()
    physical = hc.select_qubits(errors, a.edges())
    transpiled = transpile_and_verify(a, physical)
    qasm = {c.name: a.dump(c) for c in transpiled}
    record = {
        "dry_run": not ctx.real,
        "backend": a.name,
        "calibration_timestamp": a.calibration_timestamp(),
        "selected_physical_qubits": physical,
        "selected_readout_errors": [errors[q] for q in physical],
        "median_readout_error": statistics.median(errors[q] for q in physical),
        "transpiled_qasm3": qasm,
        "transpiled_sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in qasm.items()},
        "sampler_options": a.options_record(),
        "terms_check": terms,
        "authorization": ctx.load(AUTH),
        "registration": reg,
        "git_head": git_head(ctx.repo) if ctx.real else None,
        "environment": environment() if ctx.real else None,
        "constants": {"cap_seconds": CAP_SECONDS, "reserve_seconds": RESERVE_SECONDS,
                      "safety": SAFETY, "pilot_shots_per_circuit": PILOT_SHOTS,
                      "q_grid": list(Q_GRID), "s_min": {str(k): v for k, v in S_MIN.items()}},
    }
    digest = rio.write_record(ctx.out, "preflight/run_manifest.json", record, ctx.clock)
    ctx.mark("preflight", "success", {"sha256": digest})
    return record


def transpile_and_verify(adapter, physical: list[int]) -> list:
    circuits = [hc.build_logical(name) for name in hc.CIRCUITS]
    transpiled = adapter.transpile(circuits, physical)
    for t in transpiled:
        hc.verify_layout(t, physical)
    return transpiled


def manifest(ctx: Context) -> dict:
    return rio.read_record(ctx.out, "preflight/run_manifest.json")


def circuits_for_run(ctx: Context) -> list:
    m = manifest(ctx)
    transpiled = transpile_and_verify(ctx.adapter, m["selected_physical_qubits"])
    for t in transpiled:
        if hashlib.sha256(ctx.adapter.dump(t).encode()).hexdigest() != m["transpiled_sha256"][t.name]:
            raise Refused(f"transpiled {t.name} differs from the preflight record")
    return transpiled


def submissions(ctx: Context, stage: str) -> list[dict]:
    return [s for s in rio.read_lines(ctx.out / "submissions.jsonl") if s["stage"] == stage]


def run_job(ctx: Context, stage: str, index: int, shots: dict, max_seconds: int, circuits) -> dict:
    """Submit (or fetch, if already submitted) one job and write its raw record."""

    rel = f"raw/{stage}_job{index}.json"
    if (ctx.out / rel).is_file():
        return rio.read_record(ctx.out, rel)
    prior = [s for s in submissions(ctx, stage) if s["job_index"] == index]
    if prior:
        job_id = prior[-1]["job_id"]
    else:
        if max_seconds < 1:
            raise Refused("no QPU seconds left within the 360-second cap")
        shot_list = [shots[c.name] for c in circuits]
        job_id = ctx.adapter.submit(circuits, shot_list, max_seconds)
        rio.append_line(ctx.out / "submissions.jsonl", {
            "stage": stage, "job_index": index, "job_id": job_id,
            "shots_per_circuit": shots, "max_execution_time": max_seconds,
            "submitted_utc": ctx.clock()})
    result = ctx.adapter.fetch(job_id)
    if result["status"] != "DONE":
        rio.write_record(ctx.out, f"raw/{stage}_job{index}_failed.json",
                         {"job_id": job_id, **result}, ctx.clock)
        raise Refused(f"job {job_id} ended as {result['status']}; run stopped")
    record = {
        "stage": stage, "job_index": index, "job_id": job_id, "backend": ctx.adapter.name,
        "circuits": [c.name for c in circuits], "shots_per_circuit": shots,
        "max_execution_time": max_seconds, "register": hc.REGISTER,
        "bit_order": "qiskit little-endian keys; rightmost character is classical bit 0",
        "counts": dict(zip([c.name for c in circuits], result["counts"], strict=True)),
        "usage_seconds": result["usage_seconds"], "metrics": result.get("metrics"),
        "fetched_utc": ctx.clock(),
    }
    for name, counts in record["counts"].items():
        if sum(counts.values()) != shots[name]:
            raise Refused(f"job {job_id}: {name} returned {sum(counts.values())} shots")
    rio.write_record(ctx.out, rel, record, ctx.clock)
    return record


def failed_jobs(ctx: Context) -> list[str]:
    return sorted(p.name for p in (ctx.out / "raw").glob("*_failed.json"))


def pilot(ctx: Context) -> dict:
    fresh = begin(ctx, "pilot", "preflight")
    if failed_jobs(ctx):
        raise Refused("a failed job exists; going on needs an owner decision")
    if not fresh and not submissions(ctx, "pilot"):
        raise Refused("interrupted pilot with no recorded job ID; needs an owner decision")
    circuits = circuits_for_run(ctx)
    shots = {c.name: PILOT_SHOTS for c in circuits}
    rec = run_job(ctx, "pilot", 0, shots, CAP_SECONDS, circuits)
    ctx.mark("pilot", "success", {"job_id": rec["job_id"]})
    return rec


def allocation(q_pilot: float, median_error: float, max_shots: int) -> dict:
    """Protocol v4 Section 14 and amendment Section 5.4-5.5, as a pure function."""

    s_pilot = PILOT_SHOTS * len(hc.CIRCUITS)
    out = {"q_pilot": q_pilot, "s_pilot": s_pilot, "median_readout_error": median_error}
    if not q_pilot > 0:
        return {**out, "go": False, "reason": "pilot reported no positive QPU seconds"}
    r = SAFETY * q_pilot / s_pilot
    s_remaining = math.floor(max(0.0, CAP_SECONDS - q_pilot - RESERVE_SECONDS) / r)
    shots = {"p4a_all0": s_remaining // 2 + s_remaining % 2, "p4a_all1": s_remaining // 2}
    grid = max((g for g in Q_GRID if g <= median_error), default=None)
    out.update({"r": r, "s_remaining": s_remaining, "shots_per_circuit": shots,
                "q_run": grid})
    if grid is None:
        return {**out, "go": False, "reason": "median readout error below 0.005 (outside planning grid)"}
    s_min = S_MIN[grid]
    margin = min(shots.values()) - s_min
    out.update({"s_min": s_min, "margin_shots": margin})
    if margin < 0:
        return {**out, "go": False, "reason": f"{min(shots.values())} shots per circuit < {s_min}"}
    n_jobs = math.ceil(max(shots.values()) / max_shots)
    plan = []
    for k in range(n_jobs):
        plan.append({c: shots[c] // n_jobs + (1 if k < shots[c] % n_jobs else 0) for c in shots})
    return {**out, "go": True, "reason": "shots per circuit reach S_min", "plan": plan}


def allocate(ctx: Context) -> dict:
    begin(ctx, "allocate", "pilot")
    pilot_rec = rio.read_record(ctx.out, "raw/pilot_job0.json")
    terms = manifest(ctx)["terms_check"]
    result = allocation(float(pilot_rec["usage_seconds"]),
                        float(manifest(ctx)["median_readout_error"]),
                        int(terms["max_shots_per_circuit"]))
    if (ctx.out / "allocation.json").is_file():  # interrupted after writing: keep the record
        if rio.read_record(ctx.out, "allocation.json") != result:
            raise Refused("existing allocation record differs from the recomputation")
        digest = rio.canonical_sha256(ctx.out / "allocation.json")
    else:
        digest = rio.write_record(ctx.out, "allocation.json", result, ctx.clock)
    ctx.mark("allocate", "success", {"sha256": digest, "go": result["go"]})
    return result


def main_stage(ctx: Context) -> list[dict]:
    begin(ctx, "main", "allocate")
    if failed_jobs(ctx):
        raise Refused("a failed job exists; going on needs an owner decision")
    alloc = rio.read_record(ctx.out, "allocation.json")
    if not alloc["go"]:
        raise Refused(f"allocation is NO-GO: {alloc['reason']}")
    circuits = circuits_for_run(ctx)
    used = float(rio.read_record(ctx.out, "raw/pilot_job0.json")["usage_seconds"])
    records = []
    for index, shots in enumerate(alloc["plan"]):
        left = math.floor(CAP_SECONDS - used)
        rec = run_job(ctx, "main", index, shots, min(MAX_EXECUTION_TIME_LIMIT, left), circuits)
        used += float(rec["usage_seconds"])
        records.append(rec)
    ctx.mark("main", "success", {"jobs": len(records), "reported_seconds_total": used})
    return records


def status(ctx: Context) -> dict:
    return {s: ("success" if ctx.has(s) else "attempt" if ctx.has(s, "attempt") else "not started")
            for s in STAGES} | {"failed_jobs": failed_jobs(ctx),
                                "index_problems": rio.verify_index(ctx.out)}


# --------------------------------------------------------------------------- IBM adapter


class IBMAdapter:
    """Run-day adapter for qiskit-ibm-runtime >= 0.50 (client-side executor Sampler).

    API verified 2026-11-19 against the IBM Quantum documentation (sampler
    input/output, sampler options, max execution time, monitor job) and
    exercised on runtime 0.52.1 in local mode with a fake backend
    (hw_adapter_smoke_v1.py).  It was never run against a real backend before
    the registered pilot.
    """

    def __init__(self, backend_name: str | None = None, backend=None, service=None):
        if backend is None:
            from qiskit_ibm_runtime import QiskitRuntimeService

            service = service or QiskitRuntimeService()
            backend = service.backend(backend_name)
        self.backend = backend
        self.service = service
        self.name = backend.name
        self._jobs: dict[str, object] = {}

    def readout_errors(self) -> dict[int, float]:
        props = self.backend.properties()
        errors: dict[int, float] = {}
        for q in range(self.backend.num_qubits):
            try:
                errors[q] = float(props.readout_error(q))
            except Exception:  # noqa: BLE001 - qubit without a reported readout error
                continue
        return errors

    def edges(self) -> list[tuple[int, int]]:
        return [tuple(e) for e in self.backend.coupling_map.get_edges()]

    def calibration_timestamp(self) -> str:
        return self.backend.properties().last_update_date.isoformat()

    def transpile(self, circuits, physical):
        from qiskit import transpile

        return transpile(circuits, self.backend, initial_layout=physical,
                         optimization_level=0, seed_transpiler=hc.TRANSPILE_SEED)

    def dump(self, circuit) -> str:
        from qiskit import qasm3

        return qasm3.dumps(circuit)

    def _sampler(self, max_seconds: int):
        from qiskit_ibm_runtime.executor_sampler import Sampler

        sampler = Sampler(mode=self.backend)
        sampler.options.twirling.enable_gates = False
        sampler.options.twirling.enable_measure = False
        sampler.options.dynamical_decoupling.enable = False
        sampler.options.max_execution_time = int(max_seconds)
        return sampler

    def options_record(self) -> dict:
        s = self._sampler(CAP_SECONDS)
        o = s.options
        return {"class": f"{type(s).__module__}.{type(s).__name__}",
                "twirling_enable_gates": o.twirling.enable_gates,
                "twirling_enable_measure": o.twirling.enable_measure,
                "dynamical_decoupling_enable": o.dynamical_decoupling.enable,
                "init_qubits": o.execution.init_qubits,
                "meas_type": o.execution.meas_type}

    def submit(self, circuits, shots: list[int], max_seconds: int) -> str:
        job = self._sampler(max_seconds).run(
            [(c, None, int(n)) for c, n in zip(circuits, shots, strict=True)])
        job_id = job.job_id()
        self._jobs[job_id] = job
        return job_id

    def fetch(self, job_id: str) -> dict:
        job = self._jobs.get(job_id) or self.service.job(job_id)
        try:
            result = job.result()
        except Exception as exc:  # noqa: BLE001 - recorded, never swallowed silently
            return {"status": "FAILED", "error": f"{type(exc).__name__}: {exc}",
                    "counts": None, "usage_seconds": None}
        counts = [dict(getattr(result[i].data, hc.REGISTER).get_counts())
                  for i in range(len(hc.CIRCUITS))]
        try:
            metrics = job.metrics()
        except Exception as exc:  # noqa: BLE001
            metrics = {"error": f"{type(exc).__name__}: {exc}"}
        return {"status": "DONE", "counts": counts, "usage_seconds": float(job.usage()),
                "metrics": metrics}


# --------------------------------------------------------------------------- CLI


def build_context(args) -> Context:
    if not args.real:
        raise SystemExit("the CLI runs only with --real; dry runs use hw_dry_run_v1.py")
    adapter = IBMAdapter(args.backend)
    return Context(repo=REPO, out=REPO / REAL_OUT, adapter=adapter, real=True,
                   today=date.today().isoformat())


def cli(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("stage", choices=(*STAGES, "status"))
    ap.add_argument("--backend", required=True)
    ap.add_argument("--real", action="store_true", help="required: this uses QPU time")
    args = ap.parse_args(argv)
    ctx = build_context(args)
    action = {"preflight": preflight, "pilot": pilot, "allocate": allocate,
              "main": main_stage, "status": status}[args.stage]
    try:
        result = action(ctx)
    except Refused as exc:
        print(f"REFUSED: {exc}")
        return 2
    text = json.dumps(result if isinstance(result, dict) else {"jobs": len(result)},
                      indent=1, default=str)
    print(text[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
