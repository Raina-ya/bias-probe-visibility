# Implementation-error log, protocol v3

Entries are appended, never edited. Each entry enters the confirmatory lock
(protocol v3, Section 10.2).

## 1. Pre-registration state asserted by registered tests (2026-11-12)

- **Found:** after writing `docs/freeze/registration_v3.json` for OSF
  registration `j67wy` (submitted 2026-11-12T08:46:30Z, registered commit
  `e8b5300`), three tests in `tests/test_freeze_v3.py` failed:
  `test_locked_splits_refused_in_this_repository`,
  `test_no_registration_record_is_shipped`, and
  `test_development_manifest_refused_without_lock`.
- **Cause:** the tests assert the state before registration (no record,
  split 10 refused). They fail by construction once a valid record exists.
  This is a test-design error, not a protocol or analysis change.
- **Constraint:** `tests/test_freeze_v3.py` is a registered pre-development
  file, so editing it would break the development lock.
- **Fix:** the file is unchanged. A new `tests/conftest.py` marks exactly
  these three tests `xfail(strict=True)` only when the full development-lock
  check passes, so they must keep failing and pytest errors if they pass. A
  new `tests/test_registration_state.py` asserts the post-registration state:
  the record's fields, files equal to the template, every registered file
  unchanged, split 10 admitted, and splits 20/30/31 refused.
- **Before:** 3 failed, 59 passed. **After:** see the test run recorded in
  the commit that adds this entry.
- **Split 20 was never instantiated.** No development or holdout seed was
  used.
