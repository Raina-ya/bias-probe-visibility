"""Registration-state handling for pre-registration tests.

Three tests in tests/test_freeze_v3.py assert the state *before* OSF
registration: no registration record exists, split 10 is refused, and the
development manifest is refused.  That file is part of the registered lock
(split_guard.PRE_DEVELOPMENT_FILES), so it cannot be edited without breaking
the lock.  Once a registration record that passes the full development-lock
check exists, those three tests are marked xfail(strict=True): they must still
fail (if they pass, the registration record is gone or invalid and pytest
reports an error).  tests/test_registration_state.py asserts the
post-registration state directly.  Logged as implementation error 1 in
docs/freeze/implementation_error_log_v3.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import split_guard  # noqa: E402

PRE_REGISTRATION_TESTS = frozenset(
    {
        "tests/test_freeze_v3.py::SplitGuardTests::test_locked_splits_refused_in_this_repository",
        "tests/test_freeze_v3.py::SplitGuardTests::test_no_registration_record_is_shipped",
        "tests/test_freeze_v3.py::ManifestTests::test_development_manifest_refused_without_lock",
    }
)


def _registered() -> bool:
    try:
        split_guard.require_development_lock(REPO)
    except split_guard.LockError:
        return False
    return True


def pytest_collection_modifyitems(config, items):
    if not _registered():
        return
    marker = pytest.mark.xfail(
        strict=True,
        reason="asserts the pre-registration state; superseded by test_registration_state.py",
    )
    for item in items:
        if item.nodeid.replace("\\", "/") in PRE_REGISTRATION_TESTS:
            item.add_marker(marker)
