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
