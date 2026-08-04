"""API rate-limiting contract tests."""

from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app


def test_api_rate_limit_blocks_repeated_requests(monkeypatch) -> None:
    monkeypatch.setenv("API_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("API_RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("API_RATE_LIMIT_WINDOW_SECONDS", "60")
    get_settings.cache_clear()
    try:
        client = TestClient(create_app())
        first = client.get("/api/health")
        second = client.get("/api/health")
        limited = client.get("/api/health")
    finally:
        get_settings.cache_clear()

    assert first.status_code == 200
    assert second.status_code == 200
    assert limited.status_code == 429
    assert limited.json()["rate_limit"]["limit"] == 2
    assert limited.headers["X-RateLimit-Remaining"] == "0"
    assert int(limited.headers["Retry-After"]) >= 1


def test_rate_limiter_does_not_mask_active_kill_switch(monkeypatch) -> None:
    from app.core.kill_switch import activate_kill_switch, reset_kill_switch

    monkeypatch.setenv("API_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("API_RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("API_RATE_LIMIT_WINDOW_SECONDS", "60")
    get_settings.cache_clear()
    client = TestClient(create_app())
    reset_kill_switch()
    activate_kill_switch("rate-limit ordering", "pytest")
    try:
        first = client.post("/api/ops/m16/readiness/write")
        second = client.post("/api/ops/m16/readiness/write")
    finally:
        reset_kill_switch()
        get_settings.cache_clear()

    assert first.status_code == 423
    assert second.status_code == 423
    assert first.json()["kill_switch"]["reason"] == "rate-limit ordering"
