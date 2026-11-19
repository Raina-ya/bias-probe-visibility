# Hardware readout amendment v1 to protocol v4

Status: **revised draft for owner review, 2026-11-19; not registered.** Nothing
here authorizes a run. No job has been submitted, no IBM Quantum account or API
key has been used, and no backend has been chosen.

This amendment and its complete execution package (Section 10) are committed
first; the OSF registration then records that commit and the SHA-256 of
`docs/hardware/package_manifest_v1.json`. No job code is written after
registration. The run additionally needs the owner's run-day authorization and
terms check (Section 9). It implements the path in [review_v1.md](review_v1.md),
Section 4, and protocol v4 Section 14. It is an addendum after release v1.0 of
the protocol-v4 study.

Evidence type of any result under this amendment: **hardware-derived**. The
question is model transportability for the synthetic E5 readout structure. A
result cannot change any registered protocol v4 endpoint or conclusion
(review_v1.md, condition 7).

## 1. Question and scope

Specification item 22 asks whether real readout has pair correlation large
enough that an independent (tensored) readout model does worse than no
correction. This amendment answers it for the edge parity <Z_i Z_j>, the term
from which every QAOA-MaxCut score in protocol v4 is built.

Only the two P4a circuits run (all qubits prepared in 0; all qubits prepared
in 1), on 8 qubits. Each circuit observes all 28 pairs at once, so the test has
m = 2 x 28 = 56 pair-preparations. P4b is not selected (protocol v4 Section 14
permits a selection of P4a/P4b circuits): its 112 circuits would divide the
same budget by 57 and add only mixed preparations 01 and 10 (Section 8).

## 2. Relevance threshold (analytic)

For a pair under one preparation, let the assignment flips have marginals q_i,
q_j and covariance c. The observed parity flips with probability
r = r_ind - 2c, where r_ind = q_i + q_j - 2 q_i q_j is what an independent
model assumes. Raw <ZZ> errs by 2r|<ZZ>|; the independent-model estimate errs
by 4|c| / (1 - 2 r_ind) |<ZZ>|. The independent model is worse than raw if and
only if c > c*, with

    c*(q_i, q_j) = r_ind (1 - 2 r_ind) / (4 (1 - r_ind)).

For c < 0 it is never worse in the feasible range. At q_i = q_j = q the
threshold corresponds to a correlation coefficient rho* of 0.495 (q = 0.005),
0.490 (0.01), 0.480 (0.02) and 0.448 (0.05). For comparison, the largest E5
grid value (marginal 0.10, tau = 0.01) is rho = 0.11, a factor 3.5 below c*.
Code: `experiments/hardware/hw_stats_v1.py`; checks in
`tests/test_readout_power_v1.py` and `tests/test_hw_readout_v1.py`.

## 3. Statistics (frozen)

For each of the 56 pair-preparations, form the 2x2 table of flips
(n00, n01, n10, n11) from the main-stage counts summed over jobs; a flip is an
outcome differing from the prepared bit, and in n01/n10 the first digit is the
lower logical index. Let q_i_hat, q_j_hat, c_hat be the plug-in marginal rates
and covariance.

1. **Relevance (registered prediction).** H0: c <= c*(q_i, q_j). Statistic
   T = c_hat - c*(q_i_hat, q_j_hat). One-sided parametric bootstrap: draw
   B = 9,999 multinomial tables of the observed size from the joint law with
   marginals q_i_hat, q_j_hat and covariance min(c*, c_max), where
   c_max = min(q_i_hat, q_j_hat) - q_i_hat q_j_hat, and set
   p = (1 + #{T_b >= T}) / (B + 1).
2. **Detection (secondary, no directional prediction).** H0: c = 0. Two-sided
   Fisher exact test conditional on the margins (Fisher 1935); the two-sided
   p-value sums the probabilities of tables no more probable than the observed
   one (agreement with `scipy.stats.fisher_exact` is tested).
3. **Multiplicity.** Holm (1979) at family-wise alpha = 0.05 over the 56
   pair-preparations, separately for each family.
4. **Estimates (reported for every pair-preparation).** c_hat, rho_hat,
   c_hat / c*, and a 95% percentile bootstrap interval for c from B = 9,999
   multinomial resamples of the observed table. The maximum upper bound over
   pairs is reported as the hardware bound on E5-type pair correlation. Flip
   rates per logical qubit are reported for both preparations.

Bootstrap seeds: `SeedSequence([20261111, 60, 7, 5, 40, 8, 0, pair_index,
preparation, 0, test])`, where split code 60 is added by this amendment for
hardware analysis (99 in dry runs), pair_index runs over the 28 pairs in
lexicographic order of logical indices, preparation is 0 (all-0) or 1 (all-1),
and test is 0 (relevance) or 1 (interval). A table with a zero margin gives
p = 1 for both tests and is reported as uninformative for relevance.
Pilot counts are reported but excluded from the tests.

## 4. Prediction (registered)

**H-R1: no pair-preparation rejects H0 of Section 3.1 at Holm alpha = 0.05.**
That is, for no edge parity is the independent readout model worse than no
correction. H-R1 is falsified if any pair-preparation is rejected.

Basis: in protocol v4, the readout structures produced no CI-only false
certification on the holdout, and the E5 grid lies a factor 3.5 below c*.
Neither is hardware evidence. No prediction is made for the detection family.

Either outcome is informative: a rejection identifies a pair whose correlation
breaks tensored mitigation for that parity; no rejection, with the planning
power of Section 6, bounds the correlation per pair (Section 3.4).

## 5. Execution (frozen; `experiments/hardware/hw_runner_v1.py`)

1. **Stages.** `preflight`, `pilot`, `allocate`, `main`, each run by the owner
   as its own command with `--real --backend <name>`, each at most once. Every
   stage writes an attempt marker first and a success marker last under
   `results/hardware_v1/markers/`. A second run of a successful stage is
   refused. Real mode writes only to `results/hardware_v1/`; dry runs never do.
2. **Preflight checks, before any marker or submission.**
   (a) `docs/hardware/authorization_v1.json` names this backend and today's
   date and carries the exact statement of Section 9;
   (b) `docs/hardware/terms_check_v1.json` is dated today, lists its sources,
   states the allowance, the resource-unit conversion and the provider's
   maximum shots per circuit, and has `allows_run: true`;
   (c) `docs/hardware/registration_hw_v1.json` names an OSF record, its commit
   is an ancestor of HEAD, and `package_manifest_v1.json` has the registered
   SHA-256 with every listed file unchanged.
   Any failure refuses the run with nothing written, so it can be corrected.
3. **Qubit selection.** From the backend's reported readout errors at
   submission time, start from the qubit with the smallest error and grow a
   connected set in the coupling map by repeatedly adding the neighbour with
   the smallest error, until 8 qubits are selected; ties go to the lower index;
   qubits without a reported error are skipped. Logical qubit k runs on the
   k-th selected physical qubit.
4. **Circuits and bit order.** Logical qubit k is measured into bit k of the
   classical register `c`. Circuits are transpiled with that initial layout,
   optimization level 0 and seed 20261111; the runner refuses unless each
   measurement maps physical qubit k to bit k, `p4a_all1` applies one X per
   selected qubit, `p4a_all0` applies none, and no other operation appears.
   The transpiled circuits are stored as OpenQASM 3 with their SHA-256, and
   later stages refuse if re-transpiling gives a different circuit. Qiskit
   count keys are little-endian (rightmost character = bit 0); the analysis
   reverses each key so that character k is logical qubit k. This was verified
   on Qiskit's BasicSimulator (tests) and on the IBM runtime's local mode with
   the FakeTorino device snapshot (Section 10).
5. **Sampler.** qiskit-ibm-runtime >= 0.50 with the client-side
   `qiskit_ibm_runtime.executor_sampler.Sampler`; gate and measurement
   twirling and dynamical decoupling are set off explicitly (in runtime 0.52.1
   the twirling defaults are unset, not false), and the options actually used
   are recorded. Each job sets `max_execution_time` to the whole seconds left
   of the 360-second cap after all earlier reported usage. The run uses its own
   virtual environment: qiskit-ibm-runtime 0.52.1 requires Qiskit >= 2.3, while
   the test environment pins Qiskit 2.2.3; the versions used are recorded.
6. **Pilot.** The two P4a circuits at 1,000 shots each, one job. Record
   S_pilot = 2,000 and the reported QPU seconds q_pilot (`job.usage()`;
   `job.metrics()` is stored as returned).
7. **Allocation.** Protocol v4 Section 14 formula:
   r = 1.25 q_pilot / S_pilot, S_remaining = floor(max(0, 360 - q_pilot - 30) / r),
   split equally over the two circuits (remainder to `p4a_all0`). If the
   provider's maximum shots per circuit is below the allocation, the shots are
   split evenly over the fewest jobs that respect it. A pilot reporting no
   positive QPU seconds is NO-GO (time per shot unmeasurable).
8. **Go rule after the pilot.** Let q_run be the median reported readout error
   of the 8 selected qubits, rounded down to the planning grid
   {0.005, 0.01, 0.02, 0.05}. Continue only if q_run >= 0.005 and the shots per
   circuit reach S_min(q_run) from Section 6: 30,000 (0.005), 10,000 (0.01),
   10,000 (0.02), 3,000 (0.05). Rounding down is conservative: a median of
   0.0097 uses the 0.005 row. Otherwise stop: the pilot is reported and the
   tests are not run. The reduction order of protocol v4 (shots first, then
   width) does not apply, because fewer shots or qubits cannot meet S_min. The
   allocation record reports the margin to S_min in shots.
9. **Interruption and failure.** The job ID is recorded before the runner
   waits for a result. An interrupted stage resumes only the frozen plan: a
   recorded job is fetched by its ID and never resubmitted; a planned job not
   yet submitted may be submitted. A job that fails or is cancelled writes a
   failure record and stops the run; going on needs a documented owner
   decision outside the runner. A job whose returned shots differ from the
   requested shots also stops the run.
10. **Records.** Every record is written once with exclusive create and listed
    with its SHA-256 in `results/hardware_v1/index.jsonl`; job submissions are
    appended to `submissions.jsonl`. The preflight run manifest records the
    backend, calibration timestamp, selected qubits and their reported errors,
    transpiled circuits, sampler options, terms check, authorization,
    registration, git HEAD, and the Python, NumPy (with `numpy.show_config`),
    SciPy, Qiskit and qiskit-ibm-runtime versions and platform. Each raw
    record holds the job ID, shots, counts exactly as returned, reported usage
    and metrics. The analysis (`hw_analysis_v1.py`) verifies the index first and
    writes to `results/hardware_v1_analysis/`.

## 6. Planning power (simulation only, split 99)

`experiments/hardware/readout_power_v1.py` (1,000 repeats per cell; bootstrap
B = 1,999 in planning) simulates one affected pair-preparation with
q_i = q_j = q and tests it at the Holm first-step level 0.05/56. Results are in
`readout_power_v1.csv` and `.json`, produced with NumPy 2.3.4 (the CI pin).
Planning results are never reported as results.

Smallest shots per circuit with power >= 0.8:

| q | Relevance at c = 1.5 c* | Detection rho = 0.05 | rho = 0.10 | rho = 0.20 |
|---|---:|---:|---:|---:|
| 0.005 | 30,000 | 30,000 | 30,000 | 10,000 |
| 0.01 | 10,000 | 30,000 | 10,000 | 3,000 |
| 0.02 | 10,000 | 30,000 | 10,000 | 3,000 |
| 0.05 | 3,000 | 10,000 | 3,000 | 1,000 |

Detection of rho = 0.02 does not reach 0.8 within 30,000 shots at any q.
Size: with no correlation the largest rejection rate over cells is 0.001
(1 in 1,000); at the relevance boundary c = c* it is 0.003 in one cell, and
8 of 24,000 pooled over cells (0.0003), against a nominal 0.05/56 = 0.0009.
The frozen analysis uses B = 9,999.

The first planning run used NumPy 2.5.3. Under NumPy 2.3.4, 9 of 168 rows
differ by 1 to 3 rejections in 1,000 (different random streams); the table
above and the size statements other than the pooled count (7 of 24,000 under
2.5.3) are identical. The 2.5.3 outputs are kept as
`readout_power_v1_numpy2.5.3.*`. Running the pre-refactor and refactored code
under NumPy 2.3.4 gives byte-identical output.

Checks of the planning code: exact enumeration of all 2x2 tables gives
detection power 0.246 (q = 0.05, rho = 0.2, 300 shots) and 0.272 (q = 0.05,
rho = 0.1, 1,000 shots), against simulated 0.256 and 0.247 (within 2 Monte
Carlo standard errors). A normal approximation for c_hat needs fewer shots
(for example 3,000 instead of 10,000 at q = 0.01, rho = 0.1); it is not used,
because the expected count of joint flips is below 1 in that regime.

## 7. Reporting

The paper (as a v4.1 addendum) and a results note report: the terms check, the
qubit list, all job records, the go decision after the pilot, both test
families with Holm-adjusted decisions, every estimate, and the bound of
Section 3.4. If the go rule stops the run, that is reported as the outcome. The
result is labelled hardware-derived and exploratory with respect to protocol v4
endpoints.

## 8. Limitations

- Only preparations 00 and 11 are tested; correlation that appears only for
  mixed preparations, or depends on the state of other qubits, is not
  measured.
- One backend, one calibration window, one day. Drift within the run is not
  modelled; the counts are treated as independent and identically distributed.
- Planning power assumes equal marginals; real pairs have unequal q_i, q_j.
- The relevance threshold is for the edge parity under a fixed preparation;
  other observables have other thresholds.
- Qubits are chosen for low readout error, which favours a no-rejection
  outcome; greedy connected growth can still include a qubit with a larger
  error (in the FakeTorino smoke test it picked errors up to 0.050).
- The IBM adapter was exercised only in the runtime's local mode, which reports
  zero usage; the registered pilot is its first run against a real backend.

## 9. Owner authorization and run-day inputs (filled by the owner)

On the run day, after release v1.0 and after this package has passed review and
been registered, the owner copies the templates in `docs/hardware/` and fills:

- `authorization_v1.json`: backend, run date, signer, signing date, and this
  statement, copied exactly: "I authorize one run under hardware readout
  amendment v1, using at most 360 reported QPU seconds."
- `terms_check_v1.json`: the IBM Quantum terms read that day.
- `registration_hw_v1.json`: the OSF record of this package.

The owner runs the commands on their own machine with their own account, saved
by `QiskitRuntimeService`. The API key is never shared with, requested by, or
written by the assistant, and no file of this package reads or stores it.

## 10. Package and provenance

| Part | File |
|---|---|
| Statistics | `experiments/hardware/hw_stats_v1.py` |
| Circuits, bit order, qubit selection, layout check | `experiments/hardware/hw_circuits_v1.py` |
| Write-once records and index | `experiments/hardware/hw_rawio_v1.py` |
| Preflight, pilot, allocation, main; IBM adapter | `experiments/hardware/hw_runner_v1.py` |
| Analysis | `experiments/hardware/hw_analysis_v1.py` |
| Offline dry run (synthetic device; split 99) | `experiments/hardware/hw_dry_run_v1.py` -> `dry_run/` |
| IBM adapter smoke test (runtime 0.52.1 local mode, FakeTorino) | `experiments/hardware/hw_adapter_smoke_v1.py` -> `adapter_smoke/` |
| Planning power | `experiments/hardware/readout_power_v1.py` |
| Tests | `tests/test_hw_readout_v1.py`, `tests/test_readout_power_v1.py` |
| Artifact registry and check | `artifact_registry_hw_v1.yaml`, `src/provenance_hw_v1.py` |
| Package manifest (hashed by the OSF registration) | `experiments/hardware/hw_package_manifest_v1.py` -> `docs/hardware/package_manifest_v1.json` |
| Run-day input templates | `docs/hardware/*.template.json` |

The registry check also requires each artifact's name to appear in its
generator's declared `OUTPUTS`. The dry run (two scenarios: independent flips;
covariance 1.5 c* on logical pair 0-1) is byte-reproducible under NumPy 2.3.4;
it allocated GO with 3 main jobs of about 34,900 shots per circuit, found no
relevance rejection in the null scenario and exactly the injected pair in both
preparations in the correlated scenario. The smoke test drove the same
`IBMAdapter` class through preflight, pilot (1,000 shots per circuit
returned), allocation (NO-GO on zero reported usage, as designed) and a
refused main stage; its pilot flip rates track FakeTorino's reported errors
qubit by qubit, which checks the bit order and layout on the IBM software
stack. Neither is a result, and the smoke test is not bit-reproducible (the
local simulator is unseeded); its registered outputs are kept as produced.

Order of work: generate outputs; `python src/provenance_hw_v1.py --write`;
`python experiments/hardware/hw_package_manifest_v1.py --write`; tests; commit;
OSF registration of that commit and the manifest hash.

## References

- Fisher, R. A. (1935). The logic of inductive inference. *Journal of the
  Royal Statistical Society*, 98(1), 39-82. doi:10.2307/2342435.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure.
  *Scandinavian Journal of Statistics*, 6, 65-70.
- IBM Quantum documentation, read 2026-11-19: Sampler inputs and outputs
  (client-side executor Sampler from qiskit-ibm-runtime 0.50.0), Sampler
  options (`max_execution_time` 1-10,800 s; twirling and dynamical decoupling),
  Maximum execution time (QPU usage, forced cancellation), Monitor a job
  (`job.usage()` in seconds; `service.job(job_id)`). Pages at
  https://quantum.cloud.ibm.com/docs/en/guides/.
