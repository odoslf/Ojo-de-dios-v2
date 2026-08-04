"""Global kill-switch and centralized secret-redaction contract tests."""

from fastapi.testclient import TestClient

from app.core.kill_switch import activate_kill_switch, reset_kill_switch
from app.core.secret_redaction import REDACTED, redact_json_text, redact_value
from app.db.repositories.audit_log_repository import AuditLogRepository
from app.db.session import create_engine_from_url, create_session_factory, get_session, init_db
from app.main import create_app


def test_global_kill_switch_middleware_blocks_unsafe_non_exempt_routes() -> None:
    client = TestClient(create_app())
    reset_kill_switch()
    activate_kill_switch("security freeze", "pytest")
    try:
        blocked = client.post("/api/ops/m16/readiness/write")
        status = client.get("/api/kill-switch/status")
        reset_response = client.post("/api/kill-switch/reset")
    finally:
        reset_kill_switch()

    assert blocked.status_code == 423
    assert blocked.json()["kill_switch"]["reason"] == "security freeze"
    assert status.status_code == 200
    assert status.json()["active"] is True
    assert reset_response.status_code == 200
    assert reset_response.json()["active"] is False


def test_global_kill_switch_does_not_block_auth_routes(tmp_path) -> None:
    engine = create_engine_from_url(f"sqlite:///{tmp_path / 'auth-exempt.sqlite3'}")
    init_db(engine)
    session_factory = create_session_factory(engine)

    def override_session():
        with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    reset_kill_switch()
    activate_kill_switch("auth remains reachable", "pytest")
    try:
        response = client.post("/api/auth/login", json={"username": "missing", "password": "wrong"})
    finally:
        reset_kill_switch()

    assert response.status_code == 401


def test_central_secret_redaction_redacts_nested_values_and_json_text() -> None:
    payload = {"api_key": "super-secret", "nested": {"note": "token=abcdef123456", "safe": "value"}}
    redacted = redact_value(payload)
    encoded = redact_json_text('{"password":"hunter2","message":"Bearer abcdef123456"}')

    assert redacted["api_key"] == REDACTED
    assert redacted["nested"]["note"] == f"token={REDACTED}"
    assert "hunter2" not in encoded
    assert "abcdef123456" not in encoded


def test_audit_log_repository_redacts_secret_metadata_and_messages(tmp_path) -> None:
    engine = create_engine_from_url(f"sqlite:///{tmp_path / 'audit-redaction.sqlite3'}")
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        event = AuditLogRepository(session).record_event(
            "security.secret_test",
            "operator supplied token=abcdef123456",
            actor_username="admin",
            metadata_json='{"api_key":"super-secret","safe":"ok"}',
        )

    assert "abcdef123456" not in event.message
    assert "super-secret" not in str(event.metadata_json)
    assert REDACTED in event.message
    assert REDACTED in str(event.metadata_json)


def test_user_management_cannot_bypass_authentication() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/auth/users",
        json={"username": "intruder", "password": "CorrectHorseBatteryStaple!", "role": "operator"},
    )

    assert response.status_code == 401


def test_kill_switch_blocks_unsafe_route_with_query_string() -> None:
    client = TestClient(create_app())
    reset_kill_switch()
    activate_kill_switch("query-string bypass check", "pytest")
    try:
        response = client.post("/api/ops/m16/readiness/write?force=true")
    finally:
        reset_kill_switch()

    assert response.status_code == 423
    assert response.json()["kill_switch"]["reason"] == "query-string bypass check"
