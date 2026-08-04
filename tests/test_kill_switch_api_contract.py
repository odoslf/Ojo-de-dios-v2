"""Kill switch API contract tests."""

from fastapi.testclient import TestClient

from app.main import create_app


def test_kill_switch_api_lifecycle() -> None:
    client = TestClient(create_app())

    initial_response = client.get("/api/kill-switch/status")
    assert initial_response.status_code == 200
    assert initial_response.json()["active"] in {False, True}

    activate_response = client.post(
        "/api/kill-switch/activate",
        json={"reason": "test", "activated_by": "tester"},
    )
    assert activate_response.status_code == 200
    activated = activate_response.json()
    assert activated["active"] is True
    assert activated["reason"] == "test"

    status_response = client.get("/api/kill-switch/status")
    assert status_response.status_code == 200
    assert status_response.json()["active"] is True

    reset_response = client.post("/api/kill-switch/reset")
    assert reset_response.status_code == 200
    assert reset_response.json()["active"] is False
