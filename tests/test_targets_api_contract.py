"""Contract tests for target API routes."""

from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_session, init_db
from app.main import create_app


def test_targets_api_create_read_list_plan_workspace_context_refresh_and_not_available_actions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)

    create_response = client.post(
        "/api/targets/create",
        json={"name": "Example", "target_type": "domain", "value": "HTTPS://Example.COM/path"},
    )
    assert create_response.status_code == 200
    create_payload = create_response.json()
    assert "target" in create_payload
    assert "fingerprint" in create_payload
    assert create_payload["target"]["normalized_value"] == "example.com"
    assert create_payload["fingerprint"]["tags"] == ["domain"]
    target_id = create_payload["target"]["target_id"]

    get_response = client.get(f"/api/targets/{target_id}")
    assert get_response.status_code == 200
    assert get_response.json()["target"]["target_id"] == target_id

    list_response = client.get("/api/targets")
    assert list_response.status_code == 200
    assert list_response.json()["targets"]

    plan_response = client.post(f"/api/targets/{target_id}/plan")
    assert plan_response.status_code == 200
    plan_payload = plan_response.json()
    assert plan_payload["execution_started"] is False
    assert plan_payload["plan"]["status"] == "planned"
    assert plan_payload["plan"]["step_count"] > 0
    assert plan_payload["plan"]["runnable_step_count"] > 0

    context_response = client.get(f"/api/targets/{target_id}/context")
    assert context_response.status_code == 200
    context_payload = context_response.json()
    assert context_payload["target"]["target_id"] == target_id
    assert context_payload["runtime"]["job_runner_required_for_start"] is True

    attack_surface_response = client.get(f"/api/targets/{target_id}/attack-surface")
    assert attack_surface_response.status_code == 200
    attack_surface_payload = attack_surface_response.json()
    assert attack_surface_payload["execution_started"] is False
    assert attack_surface_payload["graph"]["node_count"] >= 2
    assert attack_surface_payload["graph"]["edge_count"] >= 1

    services_response = client.get(f"/api/targets/{target_id}/services")
    assert services_response.status_code == 200
    services_payload = services_response.json()
    assert services_payload["services"]["execution_started"] is False
    assert services_payload["services"]["endpoint_count"] == 0

    missing_workspace_response = client.get(f"/api/targets/{target_id}/workspace")
    assert missing_workspace_response.status_code == 200
    assert missing_workspace_response.json()["workspace"]["workspace_exists"] is False

    monkeypatch.chdir(tmp_path)
    workspace_response = client.post(
        f"/api/targets/{target_id}/workspace",
        json={"module_ids": ["m01_osint"], "bind_allowed_modules": False},
    )
    assert workspace_response.status_code == 200
    workspace_payload = workspace_response.json()
    assert workspace_payload["workspace"]["target_id"] == target_id
    assert workspace_payload["workspace_state"]["bound_modules"] == ["m01_osint"]
    assert workspace_payload["bindings"][0]["module_id"] == "m01_osint"

    refresh_response = client.post(f"/api/targets/{target_id}/fingerprint/refresh")
    assert refresh_response.status_code == 200
    assert refresh_response.json()["fingerprint"]["normalized_value"] == "example.com"

    for action in ("start", "stop"):
        action_response = client.post(f"/api/targets/{target_id}/{action}")
        assert action_response.status_code == 501
        assert action_response.json()["status"] == "not_available_yet"

    invalid_response = client.post(
        "/api/targets/create",
        json={"name": "Bad", "target_type": "bad_type", "value": "example.com"},
    )
    assert invalid_response.status_code in {400, 422}


def test_target_start_with_payload_runs_selected_plan_techniques() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)

    create_response = client.post(
        "/api/targets/create",
        json={"name": "Example", "target_type": "domain", "value": "example.com"},
    )
    assert create_response.status_code == 200
    target_id = create_response.json()["target"]["target_id"]

    start_response = client.post(
        f"/api/targets/{target_id}/start",
        json={"mode": "dry_run", "confirmed": False, "allowlisted_target": True},
    )
    assert start_response.status_code == 200
    payload = start_response.json()
    assert payload["execution_started"] is True
    assert payload["job"]["status"] in {"success", "partial", "failed", "manual_required"}
    assert payload["plan"]["can_execute"] is True
    assert payload["plan"]["runnable_step_count"] > 0
