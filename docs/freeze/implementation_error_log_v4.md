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

## 2. Timing pilot sampled one graph only (2026-11-13)

- **Found:** the first Task 2-2 timing pilot (`pilot` phase, commit `847fc2e`,
  Windows reference workstation) wrote 70 units, and all 70 were graph
  `development-w4-p1-g0`, the smallest width and depth. Its projection,
  `results/development_v4/timing_projection_v4.json` (1,467.9 s, 0.017 days),
  therefore priced every unit at the cheapest graph.
- **Cause:** the pilot took every 100th unit of the canonical work list, and
  the list is built from blocks of 50 graphs. Because 100 is a multiple of 50,
  every pick had graph index 0. This is a sampling-design error in a
  resource-check script. It changes no probe, threshold, tolerance, split, or
  analysis, and it used no outcome.
- **Evidence of size (split 99, not development):** on the Linux sandbox,
  units cost 0.19–0.74 s on `software_test-w4-p1-g0` and 0.39–16.8 s on
  `software_test-w8-p5-g0` (the slowest was P3 under E1). The first
  projection could therefore understate the full run by more than an order of
  magnitude.
- **Fix:**
  - The first pilot shard and its projection are kept unchanged and are not
    used.
  - A new `pilot-stratified` phase writes to
    `results/development_v4/pilot-stratified/`. It times every probe ×
    structure (E0 and the seven structures) at every width, rotates depth as a
    Latin square so every depth appears, and adds every probe × structure at
    the largest cell (w8, p5). This gives 327 units after removing duplicates.
    The choice is deterministic and uses no outcome.
  - `project_timing_v4.py` reads the stratified pilot by default and writes
    `timing_projection_stratified_v4.json`. It adds a conservative bound,
    which prices each full unit at the slowest pilot unit of its probe. The
    14-day cap decision uses this bound.
  - New tests reproduce the defect (stride 100 hits one graph) and check that
    the stratified pilot covers every width, depth, probe, structure, and the
    largest cell, and that it is deterministic.
- **Split 20 has not been instantiated.**

## 3. Registration-state test not state-aware for the confirmatory lock (2026-11-13)

- **Found:** while writing the Task 2-3 lock builder, before any confirmatory
  lock existed. `tests/test_registration_state_v4.py` asserted
  `test_no_v4_confirmatory_lock_yet` and that holdout is always refused. Both
  would fail by construction once `confirmatory_lock_v4.json` and, later,
  `registration_confirmatory_v4.json` are written.
- **Cause:** the rule adopted in entry 1 (write lock tests state-aware from the
  start) was not applied to this file's confirmatory checks. Test-design
  error; no protocol, matrix, probe, threshold, or analysis change.
- **Fix:** the file is not registered, so it is edited directly.
  - Holdout and Proposition-1 splits must be refused while no confirmatory
    registration exists, and the full confirmatory lock check must pass once
    it does.
  - Before the lock exists, no confirmatory registration may exist. Once it
    exists, the lock must record split-20 non-instantiation, and every hashed
    product must be unchanged.
- **Before/after:** no test had failed yet; the suite passes before and after
  (146 passed, 5 xfailed on the Linux workspace with the new Task 2-3 tests).
- **Split 20 has not been instantiated.**
