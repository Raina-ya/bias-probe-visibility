"""Tests for the hardware readout amendment v1 package (offline; no account or QPU)."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "experiments" / "hardware"))
sys.path.insert(0, str(REPO / "src"))

import hw_analysis_v1 as ha  # noqa: E402
import hw_circuits_v1 as hc  # noqa: E402
import hw_dry_run_v1 as hd  # noqa: E402
import hw_rawio_v1 as rio  # noqa: E402
import hw_runner_v1 as hr  # noqa: E402
import hw_stats_v1 as st  # noqa: E402

PINNED_NUMPY = "2.3.4"


# ----------------------------------------------------------------- bit ordering


def test_qiskit_key_conversion_reverses():
    assert hc.qiskit_key_to_internal("00000100") == "00100000"
    with pytest.raises(ValueError):
        hc.qiskit_key_to_internal("0101")


def test_bit_order_on_basic_simulator():
    from qiskit import transpile
    from qiskit.providers.basic_provider import BasicSimulator

    from qiskit import QuantumCircuit

    for k in range(hc.WIDTH):
        base = hc.build_logical("p4a_all0")
        qc = QuantumCircuit(*base.qregs, *base.cregs)
        qc.x(base.qubits[k])
        qc.compose(base, inplace=True)
        sim = BasicSimulator()
        counts = sim.run(transpile(qc, sim), shots=20, seed_simulator=1).result().get_counts()
        internal = hc.internal_counts(counts)
        assert internal == {"".join("1" if i == k else "0" for i in range(hc.WIDTH)): 20}


def test_flip_pattern_and_pair_table():
    counts = {"11111111": 5, "01111111": 3, "00111111": 2}
    assert hc.flip_pattern("01111111", "p4a_all1") == "10000000"
    assert hc.pair_table(counts, "p4a_all1", 0, 1) == [5, 0, 3, 2]
    assert hc.pair_table({"10000000": 4}, "p4a_all0", 0, 7) == [0, 0, 4, 0]
    with pytest.raises(ValueError):
        hc.pair_table(counts, "p4a_all1", 1, 0)


# ----------------------------------------------------------------- qubit selection and layout


def test_select_qubits_greedy_connected_and_ties():
    errors = {0: 0.02, 1: 0.01, 2: 0.03, 3: 0.01, 4: 0.001}
    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
    assert hc.select_qubits(errors, edges, width=3) == [4, 3, 2]
    tie = {0: 0.01, 1: 0.01, 2: 0.01}
    assert hc.select_qubits(tie, [(0, 1), (1, 2)], width=2) == [0, 1]
    with pytest.raises(ValueError):
        hc.select_qubits({0: 0.01, 1: 0.01, 2: 0.01}, [(0, 1)], width=3)


def test_layout_verified_on_generic_backend_and_mismatch_detected():
    from qiskit import transpile
    from qiskit.providers.fake_provider import GenericBackendV2

    b = GenericBackendV2(num_qubits=20, seed=7)
    errors = {q: b.target["measure"][(q,)].error for q in range(20)}
    phys = hc.select_qubits(errors, b.coupling_map.get_edges())
    for name in hc.CIRCUITS:
        t = transpile(hc.build_logical(name), b, initial_layout=phys,
                      optimization_level=0, seed_transpiler=hc.TRANSPILE_SEED)
        hc.verify_layout(t, phys)
        with pytest.raises(ValueError):
            hc.verify_layout(t, phys[::-1])


# ----------------------------------------------------------------- statistics


def test_fisher_matches_scipy_two_sided():
    from scipy.stats import fisher_exact

    rng = np.random.default_rng(np.random.SeedSequence([20261111, 99, 9, 0]))
    for _ in range(200):
        t = rng.multinomial(rng.integers(20, 3000), st.joint(0.03, 0.05, rng.uniform(0, 0.01)))
        a, b, c, d = map(int, t)  # n00, n01, n10, n11
        ours = st.fisher_two_sided(a, b, c, d)
        theirs = fisher_exact([[a, b], [c, d]], alternative="two-sided").pvalue
        assert ours == pytest.approx(theirs, rel=1e-6, abs=1e-12)


def test_holm_against_hand_example():
    reject, adj = st.holm([0.01, 0.04, 0.03, 0.005])
    assert adj == pytest.approx([0.03, 0.06, 0.06, 0.02])
    assert reject == [True, False, False, True]


def test_cstar_equalises_errors():
    qi, qj = 0.012, 0.03
    c = st.c_star(qi, qj)
    r = st.r_ind(qi, qj) - 2 * c
    assert 2 * r == pytest.approx(abs(1 - (1 - 2 * r) / (1 - 2 * st.r_ind(qi, qj))))


# ----------------------------------------------------------------- record storage


def test_records_are_write_once_and_tampering_is_detected(tmp_path):
    rio.write_record(tmp_path, "raw/a.json", {"x": 1})
    with pytest.raises(FileExistsError):
        rio.write_record(tmp_path, "raw/a.json", {"x": 2})
    assert rio.verify_index(tmp_path) == []
    (tmp_path / "raw" / "a.json").write_text('{"x": 3}\n')
    (tmp_path / "raw" / "b.json").write_text("{}\n")
    problems = rio.verify_index(tmp_path)
    assert "changed: raw/a.json" in problems and "unindexed: raw/b.json" in problems


# ----------------------------------------------------------------- allocation and go rule


def test_allocation_formula_and_go_rule():
    a = hr.allocation(q_pilot=2.5, median_error=0.012, max_shots=50000)
    assert a["r"] == pytest.approx(1.25 * 2.5 / 2000)
    assert a["s_remaining"] == math.floor((360 - 2.5 - 30) / a["r"])
    assert a["q_run"] == 0.01 and a["s_min"] == 10000 and a["go"]
    total = {c: sum(j[c] for j in a["plan"]) for c in hc.CIRCUITS}
    assert total == a["shots_per_circuit"]
    assert max(max(j.values()) for j in a["plan"]) <= 50000


def test_allocation_boundaries():
    assert not hr.allocation(0.0, 0.02, 10**6)["go"]
    assert not hr.allocation(2.5, 0.0049, 10**6)["go"]
    # q_pilot so large that shots per circuit fall below S_min for q_run = 0.02.
    big = hr.allocation(300.0, 0.02, 10**6)
    assert not big["go"] and big["margin_shots"] < 0
    # Per circuit = (330 - q) * 800 / q, so S_min = 10,000 is crossed at q = 24.44 s.
    below = hr.allocation(24.4, 0.02, 10**6)
    above = hr.allocation(24.5, 0.02, 10**6)
    assert below["go"] and min(below["shots_per_circuit"].values()) == 10019
    assert not above["go"] and min(above["shots_per_circuit"].values()) == 9975


# ----------------------------------------------------------------- runner refusals


def make_ctx(tmp_path, scenario="null", **kw):
    adapter = hd.FakeAdapter(scenario, **kw)
    return hr.Context(repo=REPO, out=tmp_path / "run", adapter=adapter, real=False,
                      today=hd.FAKE_DATE, clock=hd.fixed_clock, inputs=hd.inputs())


def test_stage_order_and_single_success(tmp_path):
    ctx = make_ctx(tmp_path)
    with pytest.raises(hr.Refused):
        hr.pilot(ctx)
    hr.preflight(ctx)
    with pytest.raises(hr.Refused):
        hr.preflight(ctx)
    with pytest.raises(hr.Refused):
        hr.allocate(ctx)
    hr.pilot(ctx)
    with pytest.raises(hr.Refused):
        hr.pilot(ctx)
    hr.allocate(ctx)
    hr.main_stage(ctx)
    with pytest.raises(hr.Refused):
        hr.main_stage(ctx)
    assert hr.status(ctx)["index_problems"] == []


@pytest.mark.parametrize("field,value", [
    ("run_date", "2025-12-31"), ("backend", "ibm_other"), ("statement", "I authorize a run."),
])
def test_authorization_mismatch_refused_before_any_marker(tmp_path, field, value):
    ctx = make_ctx(tmp_path)
    ctx.inputs["authorization_v1"][field] = value
    with pytest.raises(hr.Refused):
        hr.preflight(ctx)
    assert not (ctx.out / "markers").exists()


def test_terms_check_required(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.inputs["terms_check_v1"]["allows_run"] = False
    with pytest.raises(hr.Refused):
        hr.preflight(ctx)


def test_failed_job_stops_and_blocks(tmp_path):
    ctx = make_ctx(tmp_path, fail_job=2)  # submission 0 is the pilot; 2 is main job 1
    hr.preflight(ctx), hr.pilot(ctx), hr.allocate(ctx)
    with pytest.raises(hr.Refused, match="ended as FAILED"):
        hr.main_stage(ctx)
    with pytest.raises(hr.Refused, match="failed job"):
        hr.main_stage(ctx)
    assert (ctx.out / "raw" / "main_job1_failed.json").is_file()


def test_interrupted_job_is_fetched_not_resubmitted(tmp_path):
    ctx = make_ctx(tmp_path)
    hr.preflight(ctx)
    real_fetch = ctx.adapter.fetch
    ctx.adapter.fetch = lambda job_id: (_ for _ in ()).throw(KeyboardInterrupt())
    with pytest.raises(KeyboardInterrupt):
        hr.pilot(ctx)
    assert ctx.adapter.submitted == 1
    ctx.adapter.fetch = real_fetch
    hr.pilot(ctx)
    assert ctx.adapter.submitted == 1  # recovered by job ID, no second submission


def test_cumulative_seconds_never_exceed_cap(tmp_path):
    # Main jobs run 8x slower than the pilot predicts (about 156 s each): the third job
    # meets fewer seconds than it needs, and the per-job limit must hold the cap.
    ctx = make_ctx(tmp_path, main_slowdown=8.0)
    hr.preflight(ctx), hr.pilot(ctx)
    assert hr.allocate(ctx)["go"]
    with pytest.raises(hr.Refused):
        hr.main_stage(ctx)
    used = float(json.loads((ctx.out / "raw" / "pilot_job0.json").read_text())["usage_seconds"])
    subs = [s for s in rio.read_lines(ctx.out / "submissions.jsonl") if s["stage"] == "main"]
    assert subs
    for s in subs:
        assert used + s["max_execution_time"] <= hr.CAP_SECONDS
        raw = ctx.out / "raw" / f"main_job{s['job_index']}.json"
        if raw.is_file():
            used += float(json.loads(raw.read_text())["usage_seconds"])
    assert used <= hr.CAP_SECONDS


def test_real_mode_refuses_without_registration(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.real = True
    ctx.out = REPO / hr.REAL_OUT
    with pytest.raises(hr.Refused):
        hr.preflight(ctx)
    assert not (REPO / hr.REAL_OUT).exists()


def test_dry_run_cannot_write_real_folder(tmp_path):
    ctx = make_ctx(tmp_path)
    ctx.out = REPO / hr.REAL_OUT
    with pytest.raises(hr.Refused):
        hr.preflight(ctx)


def test_cli_requires_real_flag():
    with pytest.raises(SystemExit):
        hr.cli(["status", "--backend", "ibm_x"])


# ----------------------------------------------------------------- analysis and dry run


def test_analysis_detects_injected_correlation_only(tmp_path):
    ctx = make_ctx(tmp_path, scenario="correlated")
    hr.preflight(ctx), hr.pilot(ctx), hr.allocate(ctx), hr.main_stage(ctx)
    result = ha.run(ctx.out, tmp_path / "analysis", dry_run=True, boot=1999)
    flagged = {(tuple(r["pair"]), r["circuit"]) for r in result["pairs"] if r["relevance_reject"]}
    assert flagged == {((0, 1), "p4a_all0"), ((0, 1), "p4a_all1")}
    assert result["H_R1"].startswith("falsified")


def test_analysis_excludes_pilot_and_needs_main(tmp_path):
    ctx = make_ctx(tmp_path)
    hr.preflight(ctx), hr.pilot(ctx)
    with pytest.raises(ValueError, match="main stage"):
        ha.main_counts(ctx.out)


@pytest.mark.skipif(np.__version__ != PINNED_NUMPY, reason="dry-run hashes are for NumPy 2.3.4")
def test_committed_dry_run_reproduces(tmp_path):
    committed = json.loads((REPO / "experiments/hardware/dry_run/dry_run_v1_summary.json").read_text())
    fresh = hd.run(REPO, tmp_path / "dry")
    assert fresh == committed


def test_committed_dry_run_outcomes():
    s = json.loads((REPO / "experiments/hardware/dry_run/dry_run_v1_summary.json").read_text())
    assert s["scenarios"]["null"]["relevance_rejections"] == 0
    assert s["scenarios"]["correlated"]["relevance_rejected_pairs"] == [
        [0, 1, "p4a_all0"], [0, 1, "p4a_all1"]]
    for v in s["scenarios"].values():
        assert v["index_problems"] == [] and v["allocation"]["go"]


def test_committed_adapter_smoke_outcome():
    s = json.loads((REPO / "experiments/hardware/adapter_smoke/adapter_smoke_v1.json").read_text())
    assert s["sampler_options"]["twirling_enable_measure"] is False
    assert s["sampler_options"]["twirling_enable_gates"] is False
    assert s["sampler_options"]["dynamical_decoupling_enable"] is False
    assert s["pilot_shots_returned"] == {"p4a_all0": 1000, "p4a_all1": 1000}
    assert s["allocation_go"] is False and s["main_refused"]
    assert s["index_problems"] == []


# ----------------------------------------------------------------- registry and package manifest


def test_hw_registry_verifies_including_declared_outputs():
    import provenance_hw_v1 as ph

    assert ph.check(REPO, ph.load(REPO)) == []


def test_hw_registry_flags_wrong_generator():
    import copy

    import provenance_hw_v1 as ph

    registry = copy.deepcopy(ph.load(REPO))
    entry = next(e for e in registry["artifacts"] if e["path"].endswith("dry_run_v1_summary.json"))
    entry["generator"] = "experiments/hardware/hw_analysis_v1.py"
    assert any("does not declare" in err for err in ph.check(REPO, registry))


def test_package_manifest_matches_files():
    import hw_package_manifest_v1 as pm

    assert pm.check(REPO) == []
    files = json.loads((REPO / pm.MANIFEST).read_text())["files"]
    for required in ("experiments/hardware/hw_runner_v1.py", "docs/hardware/amendment_readout_v1.md",
                     "tests/test_hw_readout_v1.py", "artifact_registry_hw_v1.yaml"):
        assert required in files


def test_runner_constants_match_amendment():
    text = (REPO / "docs/hardware/amendment_readout_v1.md").read_text(encoding="utf-8")
    assert hr.STATEMENT in " ".join(text.split())
    for q, s in hr.S_MIN.items():
        assert f"{s:,}" in text
    assert hr.CAP_SECONDS == 360 and hr.RESERVE_SECONDS == 30 and hr.PILOT_SHOTS == 1000


def test_allocate_resumes_after_record_written(tmp_path):
    ctx = make_ctx(tmp_path)
    hr.preflight(ctx), hr.pilot(ctx)
    first = hr.allocate(ctx)
    (ctx.out / "markers" / "allocate.success").unlink()  # simulate a crash before the marker
    assert hr.allocate(ctx) == first


def test_environment_record_is_json_serialisable():
    json.dumps(hr.environment())
