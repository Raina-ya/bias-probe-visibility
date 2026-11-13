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
    for item in items:
        if item.nodeid.replace("\\", "/") in PRE_REGISTRATION_TESTS_V4:
            item.add_marker(marker)
