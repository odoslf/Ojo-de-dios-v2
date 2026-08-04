"""Version lock repository contract tests."""

from sqlalchemy import create_engine, inspect

from app.core.version_lock import (
    RUNTIME_CUSTOM,
    VERSION_LOCK_STATUS_LOCKED,
    VERSION_LOCK_STATUS_MISSING,
    VERSION_LOCK_STATUS_NEEDS_REVIEW,
    create_needs_review_entry,
)
from app.db.repositories.version_lock_repository import VersionLockRepository
from app.db.session import create_session_factory, init_db


def _session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'version-lock.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return engine, session_factory()


def test_init_db_creates_version_locks_table(tmp_path) -> None:
    engine, _ = _session(tmp_path)
    inspector = inspect(engine)

    assert "version_locks" in inspector.get_table_names()


def test_mark_missing_creates_record_and_get_by_tool_id_recovers_it(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = VersionLockRepository(session)

    model = repository.mark_missing("tool-1", "Tool One", "module-1", "1.0.0", RUNTIME_CUSTOM)
    session.commit()
    recovered = repository.get_by_tool_id("tool-1")

    assert model.status == VERSION_LOCK_STATUS_MISSING
    assert recovered is not None
    assert recovered.tool_id == "tool-1"


def test_mark_locked_updates_same_tool_id_to_locked(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = VersionLockRepository(session)
    missing = repository.mark_missing("tool-1", "Tool One", "module-1", "1.0.0", RUNTIME_CUSTOM)
    session.commit()

    locked = repository.mark_locked("tool-1", "Tool One", "module-1", "1.0.0", "1.0.0", RUNTIME_CUSTOM)
    session.commit()
    recovered = repository.get_by_tool_id("tool-1")

    assert locked.id == missing.id
    assert recovered.status == VERSION_LOCK_STATUS_LOCKED
    assert recovered.resolved_version == "1.0.0"


def test_mark_needs_review_updates_same_tool_id(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = VersionLockRepository(session)
    repository.mark_locked("tool-1", "Tool One", "module-1", "1.0.0", "1.0.0", RUNTIME_CUSTOM)
    session.commit()

    reviewed = repository.mark_needs_review("tool-1", "Tool One", "module-1", "latest-release-lock")
    session.commit()

    assert reviewed.status == VERSION_LOCK_STATUS_NEEDS_REVIEW
    assert reviewed.resolved_version == ""


def test_list_by_module_returns_module_records(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = VersionLockRepository(session)
    repository.mark_missing("tool-b", "Bravo", "module-1", "1.0.0", RUNTIME_CUSTOM)
    repository.mark_missing("tool-a", "Alpha", "module-1", "1.0.0", RUNTIME_CUSTOM)
    repository.mark_missing("tool-c", "Charlie", "module-2", "1.0.0", RUNTIME_CUSTOM)
    session.commit()

    history = repository.list_by_module("module-1")

    assert [item.tool_id for item in history] == ["tool-a", "tool-b"]


def test_list_all_returns_records(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = VersionLockRepository(session)
    repository.mark_missing("tool-b", "Bravo", "module-2", "1.0.0", RUNTIME_CUSTOM)
    repository.mark_missing("tool-a", "Alpha", "module-1", "1.0.0", RUNTIME_CUSTOM)
    session.commit()

    records = repository.list_all()

    assert [item.tool_id for item in records] == ["tool-a", "tool-b"]


def test_upsert_lock_does_not_duplicate_tool_id(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = VersionLockRepository(session)
    repository.upsert_lock(create_needs_review_entry("tool-1", "Tool One", "module-1", "1.0.0"))
    repository.upsert_lock(create_needs_review_entry("tool-1", "Tool One Updated", "module-1", "1.1.0"))
    session.commit()

    records = repository.list_all()

    assert len(records) == 1
    assert records[0].tool_name == "Tool One Updated"
    assert records[0].recommended_version == "1.1.0"


def test_module_scoped_tool_ids_do_not_collide_between_modules(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = VersionLockRepository(session)
    repository.mark_missing("m01_osint/nmap", "Nmap", "m01_osint", "unresolved", RUNTIME_CUSTOM)
    repository.mark_missing("m02_vulnerabilities/nmap", "Nmap", "m02_vulnerabilities", "unresolved", RUNTIME_CUSTOM)
    session.commit()

    assert len(repository.list_all()) == 2
    assert [item.tool_id for item in repository.list_by_module("m01_osint")] == ["m01_osint/nmap"]
    assert [item.tool_id for item in repository.list_by_module("m02_vulnerabilities")] == ["m02_vulnerabilities/nmap"]
