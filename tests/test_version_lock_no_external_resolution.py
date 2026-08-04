"""Version lock tests for non-resolving behavior."""

import inspect

import pytest

from app.core.errors import ContractError
from app.core import version_lock
from app.core.version_lock import (
    RUNTIME_CUSTOM,
    VERSION_LOCK_STATUS_LOCKED,
    VERSION_LOCK_STATUS_MISSING,
    VERSION_LOCK_STATUS_NEEDS_REVIEW,
    create_locked_entry,
    create_missing_lock,
    create_needs_review_entry,
)
from app.db.repositories.version_lock_repository import VersionLockRepository
from app.db.session import create_session_factory, init_db
from sqlalchemy import create_engine


def _repository(tmp_path) -> VersionLockRepository:
    engine = create_engine(f"sqlite:///{tmp_path / 'version-lock-no-resolution.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return VersionLockRepository(session_factory())


def test_create_missing_lock_does_not_resolve_external_version() -> None:
    entry = create_missing_lock("tool-1", "Tool One", "module-1", "latest-release-lock", RUNTIME_CUSTOM)

    assert entry.status == VERSION_LOCK_STATUS_MISSING
    assert entry.resolved_version == ""
    assert entry.binary_hash == ""


def test_create_needs_review_with_latest_release_lock_stays_needs_review() -> None:
    entry = create_needs_review_entry("tool-1", "Tool One", "module-1", "latest-release-lock")

    assert entry.status == VERSION_LOCK_STATUS_NEEDS_REVIEW
    assert entry.resolved_version == ""


def test_mark_needs_review_does_not_invent_resolved_version(tmp_path) -> None:
    repository = _repository(tmp_path)

    model = repository.mark_needs_review("tool-1", "Tool One", "module-1", "latest-release-lock")

    assert model.status == VERSION_LOCK_STATUS_NEEDS_REVIEW
    assert model.recommended_version == "latest-release-lock"
    assert model.resolved_version == ""


def test_empty_binary_hash_is_valid_for_missing_and_needs_review() -> None:
    missing = create_missing_lock("tool-1", "Tool One", "module-1", "1.0.0")
    needs_review = create_needs_review_entry("tool-2", "Tool Two", "module-1", "1.0.0")

    assert missing.status == VERSION_LOCK_STATUS_MISSING
    assert missing.binary_hash == ""
    assert needs_review.status == VERSION_LOCK_STATUS_NEEDS_REVIEW
    assert needs_review.binary_hash == ""


def test_locked_requires_explicit_resolved_version() -> None:
    with pytest.raises(ContractError):
        create_locked_entry("tool-1", "Tool One", "module-1", "1.0.0", "", RUNTIME_CUSTOM)


def test_no_public_external_resolution_functions_exist() -> None:
    public_functions = {
        name
        for name, value in inspect.getmembers(version_lock, inspect.isfunction)
        if not name.startswith("_")
    }

    assert "resolve_latest_release" not in public_functions
    assert "download_release" not in public_functions
    assert "run_tool_version" not in public_functions
    assert "execute_version_command" not in public_functions
