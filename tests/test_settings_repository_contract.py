"""Settings and audit log repository contract tests."""

from app.db.repositories.audit_log_repository import AuditLogRepository
from app.db.repositories.settings_repository import SettingsRepository
from app.db.session import create_engine_from_url, create_session_factory, init_db


def test_settings_repository_creates_updates_and_returns_defaults(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'settings_test.sqlite3'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        repository = SettingsRepository(session)

        created = repository.set_value("app.mode", "demo", "Current mode")
        updated = repository.set_value("app.mode", "controlled", "Updated mode")

        assert created.id == updated.id
        assert repository.get_value("app.mode") == "controlled"
        assert repository.get_value("missing", "fallback") == "fallback"
        assert [setting.key for setting in repository.list_settings()] == ["app.mode"]


def test_audit_log_repository_records_events_and_limits_recent_results(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'audit_log_test.sqlite3'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        repository = AuditLogRepository(session)
        repository.record_event("settings.updated", "Updated settings", actor_username="admin")
        repository.record_event("users.created", "Created user", metadata_json='{"role":"admin"}')

        recent = repository.list_recent(limit=1)

        assert len(recent) == 1
        assert recent[0].event_type in {"settings.updated", "users.created"}
