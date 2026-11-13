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
