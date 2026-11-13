# Implementation error log, protocol v4, after the confirmatory lock

`docs/freeze/implementation_error_log_v4.md` (entries 1-3) is hashed in
`confirmatory_lock_v4.json` (OSF `j597k`) and is therefore closed. Entries made
after the lock are recorded here, continuing the numbering. The same rules
apply: an entry may fix only an implementation or test-design error, never a
scientific mismatch, and it changes no protocol, matrix, probe, threshold, or
analysis rule.

## 4. Two registered tests assert the pre-confirmatory state (2026-11-13)

- **Found:** before writing `registration_confirmatory_v4.json` (OSF `j597k`,
  approved and public), by running the suite with the record present.
  `tests/test_execution.py::LockTests::test_runner_refuses_holdout` and
  `tests/test_v4.py::LockV4Tests::test_v4_registration_admits_development_only`
  assert that the holdout is refused. That is true only before the
  confirmatory registration exists; with the record present both fail
  (144 passed, 2 failed).
- **Cause:** same class as entry 1. Both files are in the registered lock
  (`PRE_DEVELOPMENT_FILES_V4`) and cannot be edited without breaking it.
- **Fix:** the root `conftest.py` (not registered) marks the two tests
  xfail(strict=True) once the full confirmatory-lock check passes. They must
  still fail; if either passes, the confirmatory record is gone or invalid and
  pytest reports an error. `tests/test_registration_state_v4.py` asserts the
  post-confirmatory state directly (entry 3).
- **Before/after:** with the record present, 144 passed, 7 xfailed; without
  it, 146 passed, 5 xfailed (Linux workspace).
- **Split 20 has not been instantiated.**

## 5. Test states after the single holdout run (2026-11-13, before split 20)

- **Found:** while writing the Task 3-1 holdout driver, before split 20 was
  instantiated. After the run writes `results/run_markers_v4/holdout.success`,
  the split guard refuses the holdout again. Then
  `tests/test_execution.py::LockTests::test_runner_refuses_holdout`, which
  entry 4 marks xfail(strict=True), would pass, and strict xfail would report
  an error. Two new tests in `tests/test_holdout_v4.py` assumed the marker was
  absent.
- **Cause:** test-design error of the same class as entries 1, 3, and 4: tests
  not written for every registration state. No protocol, matrix, probe,
  threshold, or analysis change.
- **Fix:** the root `conftest.py` stops marking that runner test once the
  marker exists. The copied-repository test excludes `results/`, so it still
  sees an open holdout and stays xfail. The two new tests branch on the marker.
- **Before/after:** before the run, 160 passed and 7 xfailed on the Linux
  workspace. The post-run branches are not exercised before the run, because
  exercising them would build the split-20 manifest; they are checked by the
  first test run after `finalize`, and that result is reported.
- **Split 20 has not been instantiated.**
