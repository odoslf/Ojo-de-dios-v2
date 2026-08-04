"""HTTP route tests for the base application chassis."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_health_route_returns_minimal_status() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["product_display_name"] == "Ojo de Dios"
    assert payload["default_execution_mode"] == "demo"


def test_root_route_returns_minimal_landing_payload() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["next"] == "/modules"
