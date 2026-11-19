# Implementation-error log, hardware readout amendment v1 (OSF wh5rs)

## 1. Registered test asserts the pre-run state (2026-11-19, after the single run)

- **Found:** the full test suite, run after the registered hardware run while
  preparing paper v4.1, failed one test:
  `tests/test_hw_readout_v1.py::test_real_mode_refuses_without_registration`.
- **Cause:** test-design error of the same class as protocol-v4 entries 1, 3, 4
  and 5. The test checks that real mode is refused and then asserts that
  `results/hardware_v1/` does not exist, which holds only before the run. The
  refusal itself still holds: real-mode preflight is refused ("preflight already
  succeeded") and the real output folder is unchanged (checked file by file).
- **Constraint:** the test file is listed in
  `docs/hardware/package_manifest_v1.json`, whose SHA-256 the OSF registration
  records, so it is not edited.
- **Fix:** the root `conftest.py` (not in the manifest or any lock) marks that
  test xfail(strict=True) once `results/hardware_v1/markers/main.success`
  exists. The new `tests/test_hw_post_run_state_v1.py` asserts the post-run
  state: all four stages succeeded, the record index is intact, no failed job,
  every stage refuses a new real run without writing anything, and reported
  seconds are within the 360-second cap.
- **Before/after:** before, 1 failed, 230 passed, 2 skipped, 6 xfailed (Linux
  workspace); after, 233 passed, 2 skipped, 7 xfailed. The hardware records,
  the analysis and every file in the registered manifest are unchanged.

## 2. Dry-run byte identity does not hold on Windows (2026-11-19, after the single run)

- **Found:** the GitHub Actions `tests` workflow failed on `windows-latest` (Python 3.14,
  pinned NumPy 2.3.4, SciPy 1.16.3, Qiskit 2.2.3) from commit `64b55e1` on, while
  `ubuntu-latest` passed; the owner's Windows workstation failed the same test:
  `tests/test_hw_readout_v1.py::test_committed_dry_run_reproduces`. The release v1.0
  commit `a41dad3`, before the hardware package, passed on both.
- **Cause:** the test requires the dry-run summary to be byte-identical to the one
  produced on Linux. On Windows exactly one field differs, an `analysis_sha256`; every
  raw-record hash, selected qubit, shot count, rejection count and H-R1 verdict agrees.
  The analysis JSON therefore differs in floating-point digits. The likely source is
  the platform `math.lgamma` used in the Fisher p-values; this was not isolated. The
  amendment's statement that the dry run is "byte-reproducible under NumPy 2.3.4"
  (Section 10) holds on Linux only. This is a test-design error; the hardware run and
  its analysis are unaffected (the analysis decisions do not depend on the last digits,
  and the independent recomputation agreed).
- **Constraint:** the test file and the amendment are in the registered manifest and are
  not edited.
- **Fix:** the root `conftest.py` marks that test xfail(strict=True) on Windows only.
  The new `tests/test_hw_dry_run_cross_platform_v1.py` reruns the dry run on every
  platform and compares the summary and both analysis files field by field: non-float
  values exactly, floats to a relative tolerance of 1e-9, listing any differing field.
- **Before/after:** Linux unchanged (passing). Windows: before, 1 failed; after, the
  registered test is an expected failure and the field-by-field test is checked by CI.
