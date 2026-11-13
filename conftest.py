"""Registration-state handling for v4 pre-registration tests (repository root).

Two tests in registered v4 test files assert the state *before* the v4 OSF
registration: ``tests/test_v4.py::LockV4Tests::test_v4_refuses_development_and_holdout_without_registration``
and ``tests/test_execution.py::LockTests::test_runner_refuses_development_and_holdout_without_registration``.
Those files are in ``split_guard_v4.PRE_DEVELOPMENT_FILES_V4`` and cannot be
edited without breaking the v4 lock, and ``tests/conftest.py`` is registered
too, so this hook lives in a new root-level ``conftest.py``.  Once the full v4
development-lock check passes, the two tests are marked xfail(strict=True);
``tests/test_registration_state_v4.py`` asserts the post-registration state.
Logged as implementation error 1 in docs/freeze/implementation_error_log_v4.md.

Two further registered tests assert that the holdout is refused, which holds
only before the confirmatory registration:
``tests/test_execution.py::LockTests::test_runner_refuses_holdout`` and
``tests/test_v4.py::LockV4Tests::test_v4_registration_admits_development_only``.
Once the full confirmatory-lock check passes, they are marked
xfail(strict=True); ``tests/test_registration_state_v4.py`` asserts the
post-confirmatory state.  Logged as implementation error 4 in
docs/freeze/implementation_error_log_v4_post_lock.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "src"))

import split_guard_v4  # noqa: E402

PRE_REGISTRATION_TESTS_V4 = frozenset(
    {
        "tests/test_v4.py::LockV4Tests::test_v4_refuses_development_and_holdout_without_registration",
        "tests/test_execution.py::LockTests::test_runner_refuses_development_and_holdout_without_registration",
    }
)


PRE_CONFIRMATORY_TESTS_V4 = frozenset(
    {
        "tests/test_execution.py::LockTests::test_runner_refuses_holdout",
        "tests/test_v4.py::LockV4Tests::test_v4_registration_admits_development_only",
    }
)


RUNNER_HOLDOUT_TEST = "tests/test_execution.py::LockTests::test_runner_refuses_holdout"


def _confirmatory_v4() -> bool:
    try:
        split_guard_v4.require_confirmatory_lock(REPO)
    except (split_guard_v4.LockError, FileNotFoundError):
        return False
    return True


def _registered_v4() -> bool:
    try:
        split_guard_v4.require_development_lock(REPO)
    except split_guard_v4.LockError:
        return False
    return True


def pytest_collection_modifyitems(config, items):
    if not _registered_v4():
        return
    marker = pytest.mark.xfail(
        strict=True,
        reason="asserts the pre-v4-registration state; superseded by test_registration_state_v4.py",
    )
    confirmatory = _confirmatory_v4()
    holdout_done = split_guard_v4.marker_path(REPO, "holdout").exists()
    confirmatory_marker = pytest.mark.xfail(
        strict=True,
        reason="asserts the pre-confirmatory state; superseded by test_registration_state_v4.py",
    )
    for item in items:
        nodeid = item.nodeid.replace("\\", "/")
        if nodeid in PRE_REGISTRATION_TESTS_V4:
            item.add_marker(marker)
        elif confirmatory and nodeid in PRE_CONFIRMATORY_TESTS_V4:
            # After the single holdout run, the split guard refuses the
            # holdout again (marker present), so the runner test passes once
            # more and must not be marked (post-lock entry 5).  The copied-repo
            # test excludes results/ and therefore still sees an open holdout.
            if holdout_done and nodeid == RUNNER_HOLDOUT_TEST:
                continue
            item.add_marker(confirmatory_marker)
