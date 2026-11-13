# Implementation-error log, protocol v4

Entries are appended, never edited. Each entry enters the v4 confirmatory lock
(protocol v4, Section 10.2).

## 1. Pre-registration state asserted by registered tests (2026-11-13)

- **Found:** after writing `docs/freeze/registration_v4.json` for OSF
  registration `r63vn` (submitted 2026-11-13T01:45:49Z, registered commit
  `e3908db`), two registered tests failed:
  `tests/test_v4.py::LockV4Tests::test_v4_refuses_development_and_holdout_without_registration`
  and
  `tests/test_execution.py::LockTests::test_runner_refuses_development_and_holdout_without_registration`.
- **Cause:** both assert the state before registration, so they fail by
  construction once a valid v4 record exists. This repeats v3 implementation
  error 1; the lesson was not applied when the v4 tests were written. It is a
  test-design error, not a protocol or analysis change.
- **Constraint:** both test files and `tests/conftest.py` are registered v4
  files, so editing them would break the v4 development lock.
- **Fix:** no registered file is changed.
  - A new repository-root `conftest.py` marks exactly these two tests
    `xfail(strict=True)` only when the full v4 lock check passes, so pytest
    errors if either ever passes.
  - A new `tests/test_registration_state_v4.py` asserts the post-registration
    state: the record's fields, files equal to the template and lock list,
    every registered file unchanged, split 10 admitted, splits 20/30/31
    refused, the runner's closure and commit checks, no confirmatory lock yet,
    and the v3 record intact.
- **Before:** 2 failed, 110 passed, 3 xfailed. **After:** recorded in the commit
  that adds this entry.
- **Split 10 and split 20 have not been instantiated** for any output.
- **Rule adopted from now on:** every lock or registration test is written
  state-aware from the start. It must check the pre-registration state only
  while no record exists, and the post-registration state once one does.
