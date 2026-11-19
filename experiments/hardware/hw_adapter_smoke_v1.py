"""Offline smoke test of IBMAdapter with qiskit-ibm-runtime local mode (never a result).

Uses the runtime's FakeTorino (a device-parameter simulation built from a
public calibration snapshot) through the same IBMAdapter class as the real
run: calibration readout, qubit selection, transpilation to the IBM basis and
layout check, the client-side executor Sampler with per-circuit shots and
twirling and dynamical decoupling switched off, counts from register ``c``,
and reported usage.  Local mode reports zero usage, so allocation must stop
with NO-GO; that path is checked too.  No account, network or QPU is used.

Requires qiskit-ibm-runtime >= 0.50 and qiskit-aer (not in CI; the test that
reads this script's outputs only checks their registered hashes).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hw_circuits_v1 as hc  # noqa: E402
import hw_rawio_v1 as rio  # noqa: E402
import hw_runner_v1 as hr  # noqa: E402

OUTPUTS = ("adapter_smoke_v1.json", "adapter_smoke_v1_log.txt")
FAKE_DATE = "2026-01-01"


def run(out_root: Path) -> dict:
    from qiskit_ibm_runtime import __version__ as runtime_version
    from qiskit_ibm_runtime.fake_provider import FakeTorino

    if out_root.exists():
        raise SystemExit(f"{out_root} exists; smoke-test outputs are written once")
    backend = FakeTorino()
    adapter = hr.IBMAdapter(backend=backend)
    inputs = {
        "authorization_v1": {"backend": adapter.name, "run_date": FAKE_DATE,
                             "statement": hr.STATEMENT, "signed_by": "SMOKE TEST (no owner signature)",
                             "signed_date": FAKE_DATE},
        "terms_check_v1": {"checked_date": FAKE_DATE, "sources": ["smoke test: no terms read"],
                           "allowance": "local mode", "unit_conversion": "local mode",
                           "max_shots_per_circuit": 100000, "allows_run": True},
    }
    ctx = hr.Context(repo=hr.REPO, out=out_root / "run", adapter=adapter, real=False,
                     today=FAKE_DATE, clock=lambda: "2026-01-01T00:00:00.000000Z", inputs=inputs)
    pre = hr.preflight(ctx)
    pilot = hr.pilot(ctx)
    alloc = hr.allocate(ctx)
    try:
        hr.main_stage(ctx)
        main_refused = None
    except hr.Refused as exc:
        main_refused = str(exc)
    internal = {c: hc.internal_counts(pilot["counts"][c]) for c in hc.CIRCUITS}
    flip_rates = {
        c: [sum(n for z, n in internal[c].items() if hc.flip_pattern(z, c)[k] == "1") / hr.PILOT_SHOTS
            for k in range(hc.WIDTH)]
        for c in hc.CIRCUITS}
    return {
        "runtime_version": runtime_version,
        "backend": adapter.name,
        "selected_physical_qubits": pre["selected_physical_qubits"],
        "selected_readout_errors": pre["selected_readout_errors"],
        "sampler_options": pre["sampler_options"],
        "transpiled_op_counts": {c: {"measure": q.count(" = measure "),
                                     "x": sum(1 for line in q.splitlines() if line.startswith("x ")),
                                     "barrier": sum(1 for line in q.splitlines() if line.startswith("barrier"))}
                                 for c, q in pre["transpiled_qasm3"].items()},
        "pilot_shots_returned": {c: sum(v.values()) for c, v in pilot["counts"].items()},
        "pilot_usage_seconds": pilot["usage_seconds"],
        "pilot_flip_rates_per_logical_qubit": flip_rates,
        "allocation_go": alloc["go"], "allocation_reason": alloc["reason"],
        "main_refused": main_refused,
        "index_problems": rio.verify_index(out_root / "run"),
    }


def cli(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=hr.REPO / "experiments" / "hardware" / "adapter_smoke")
    args = ap.parse_args(argv)
    summary = run(args.out)
    (args.out / OUTPUTS[0]).write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n",
                                       encoding="utf-8", newline="\n")
    lines = [f"{k}: {v}" for k, v in summary.items() if k != "pilot_flip_rates_per_logical_qubit"]
    (args.out / OUTPUTS[1]).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
