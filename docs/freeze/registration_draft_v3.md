# Registration draft for protocol v3 (task 1d-3)

Status: draft prepared 2026-11-12. Nothing has been registered. The project
owner reviews, commits, and registers; Claude does not commit, push, or
register.

## 1. Registry choice

Use **OSF Registries**. A registration made from an OSF project archives the
files in the project's OSF Storage, cannot change those files afterwards, and
records the submission date as its creation date. It can be embargoed for up
to four years (OSF help: "Registration Files"). AsPredicted is a fallback; its
form has nine text questions (Data collection, Hypothesis, Dependent variable,
Conditions, Analyses, Outliers and exclusions, Sample size, Other, Study type)
and does not archive the protocol file, so the hashes in Section 4 would have
to be pasted into "Other".

## 2. Owner steps, in order

1. Review `docs/freeze/frozen_protocol_v3.md` in full, especially Sections 4,
   7, 11.4, and 18. Any edit changes its hash: rerun the sidecar and tests.
2. Run the test suite and the provenance check (commands in the delivery
   message). Both must pass.
3. Commit and push. Record the full commit hash.
4. Create an OSF project. Upload to its OSF Storage the files listed in
   Section 4, at the registered commit, and nothing else.
5. Register the project, pasting Section 3 into the description. Choose an
   embargo if the plan should stay private.
6. Copy `docs/freeze/registration_v3.template.json` to
   `docs/freeze/registration_v3.json`. Fill in `registry`, `url`,
   `timestamp_utc`, and `commit`, leave `files` unchanged, then commit.
7. Check `python -c "import sys; sys.path.insert(0,'src'); import split_guard, pathlib; split_guard.require_split(pathlib.Path('.'), 'development'); print('development lock OK')"`.
   Only then may Task 2-1 code be committed and split 10 be used.

## 3. Registration text

**Title.** Visibility boundary of runtime bias probes for fixed-budget
quantum-decision certification (protocol v3).

**Data collection.** No noisy simulation, device-parameter simulation, or
hardware data exist for this study. Analytic derivations, a simulated power
design, an outcome-free dry run, and noiseless design checks on a software-test
seed namespace (split 99), which is disjoint from development and holdout, were
used to write the protocol.

**Hypotheses.** The 56 primary probe-by-structure visibility labels in
`docs/theory/06_matrix.csv` (SHA-256 `7a8e3a56...d8995`; 35 blind, 15 partial, 6
visible) are falsifiable predictions for the operational statistics defined in
the protocol.

**Primary endpoint.** The fraction of the 56 cells whose observed label agrees
with the prediction, at the main operating point (largest frozen strength per
structure), on 100 holdout graphs with 32 repeats each, under a fixed budget of
16,384 shots per graph-cell-repeat. Success requires the 2.5th percentile of a
10,000-resample stratified graph-cluster bootstrap to be at least 0.80.

**Secondary and descriptive.** Bias-aware certificate versus confidence-
interval-only certification; minimum qualifying probe fraction; the
Proposition-1 raw-versus-ZNE prediction hit rate (predictions committed and
timestamped before scoring); and the descriptive decision-flip subset.

**Exclusions.** No graph is excluded for its ideal gap, noisy result, or probe
behaviour. Unattainable, invalid, and not-evaluable cells count as
disagreements. Failed runs are retained.

**Second lock.** Development (split 10) produces the strength map, E0 alarm
thresholds, a mismatch report, an implementation-error log, and a timing
pilot. These are committed and independently timestamped as
`confirmatory_lock_v3.json` before the holdout (split 20) is instantiated
once.

## 4. Files to archive (LF-normalized SHA-256)

The first 12 rows are also the `files` map in
`registration_v3.template.json`, which `split_guard` checks.

| File | SHA-256 |
|---|---|
| `docs/freeze/frozen_protocol_v3.md` | `50f68ae3455f544140f0bba114fef8b02feee7677eb676986f0efe0cf41ca513` |
| `docs/theory/06_matrix.csv` | `7a8e3a56e6f48d8a29c3643c1c2e24f46bce6a54c674d6b1937dbdcd041d8995` |
| `artifact_registry_v1.yaml` | `c45a49dce800f112dca06a06c9733776c352ae17cc2d8bc8d1c916a40d052ee9` |
| `src/hashing.py` | `265a1c4f037e871eb09698d899dbe5a7d3c329ffd2c6c1b393f9bc0a1865e68c` |
| `src/protocol_contract.py` | `fefe74173178fb3c6cd27016eab7536e5e533505470324b1e02bd0105ab52bea` |
| `src/split_guard.py` | `8c3533dd96dbe34cfbb20fdccd4a8343cae0ffbd58c0f79c325d5b0b6095662c` |
| `src/manifest.py` | `fe659495ab5e32682d24b9af451d108f563b898990f3d7e8f34735e55bedb21b` |
| `src/strength_map.py` | `bd31f0d40f472621d34bddf6169eaa750d35f0bf49b96a34014641859f8b816a` |
| `src/alarm_calibration.py` | `eca0cba5ae09c7da80811b4111a92aa333f4244d92bb33c99235845052cd8d86` |
| `src/analysis.py` | `15d009ed84125ec6b98223b0292e446729937abe3d2b42142d899b57f4bee9c4` |
| `tests/test_freeze_v3.py` | `2cf68bb196e5496e72fd05e5de17b46991d8cdd351877f85cee070f4bf2466ad` |
| `tests/test_protocol_v3.py` | `ab9c5e9f2d75945c80009c30a4f9ad845f8e9334a4946d11918bfbaf1ba88274` |
| `docs/freeze/frozen_protocol_v3.sha256` | `7f3776c54cfe72a1a48ecc2bc8869eda45593f7280de5bfed59e618e64c20e62` |
| `docs/freeze/power_analysis_v4.md` | `835f5231386f6c2c8db0fe71873a2fc8e07d4e3b2f9bae293fe1dd3d65409c32` |
| `docs/freeze/freeze_review_v2.md` | `28e87d0a0e0ac790fe47d9059a2590faecab4f3e4812b0d2fcdc5dfa3d85c5d0` |
| `experiments/power/power_analysis_raw_v4.csv` | `457c095bd811d492647b846b4bda95842e16d77f5a2961c249bba0fd1da2f8f9` |
| `experiments/power/power_analysis_summary_v4.csv` | `dcf47ddfd2e6b0847e74a2d74b28f474192538387c771b4661b9820c711fd715` |
| `experiments/power/run_log_v4.txt` | `096bee823243be6a6707050c782a9b856e34c529c63faecc0429140354c0d6df` |
| `experiments/dry_run/dry_run_ledger_v2.csv` | `09ba32711a06678bfee14d9c51e51f66a67c0ac91f42740cf7847545ec819abb` |
| `experiments/dry_run/dry_run_log_v2.txt` | `b15b3f32da6369e0c284f54096abe1d00987a5ddb37f0df0e1da07060700f23f` |
| `experiments/design_checks/readout_ratio_log.txt` | `fbc53370557902a9082fd9c39ee7d4d552a7b44b547c1b7135acc63876da2a9b` |
| `experiments/design_checks/gate_ratio_log.txt` | `a775851193cb2b6b61e6d27898d2c30f06f8aace4c4f1fdc5525e98d7a7b2839` |
