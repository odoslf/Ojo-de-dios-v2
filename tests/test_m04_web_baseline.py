"""M04 operator-observed web baseline tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m04_web_baseline import (
    read_m04_web_baseline,
    web_response_observation_from_payload,
    write_m04_web_baseline,
)
from app.core.target_model import TARGET_URL, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(
        target_id="target-m04",
        name="M04 target",
        target_type=TARGET_URL,
        value="https://example.com",
        normalized_value="https://example.com",
        mode=TARGET_MODE_DRY_RUN,
        allowed_modules=["m04_web_intrusion"],
    )


def test_m04_baseline_persists_observed_headers_without_requesting_target(tmp_path: Path) -> None:
    observation = web_response_observation_from_payload({
        "url": "https://example.com/login",
        "status_code": 200,
        "headers": {"Content-Security-Policy": "default-src 'self'", "X-Content-Type-Options": "nosniff", "Set-Cookie": "secret=value"},
    })
    path = write_m04_web_baseline(_target(), observation, repo_root=tmp_path)
    baseline = read_m04_web_baseline(_target(), repo_root=tmp_path)

    assert path.is_file()
    assert baseline is not None
    assert baseline["target_request_performed"] is False
    assert "set-cookie" not in baseline["observation"]["headers"]
    assert baseline["header_posture"]["checks"]["content_security_policy"] is True
    assert baseline["header_posture"]["checks"]["strict_transport_security"] is False


def test_m04_baseline_api_writes_and_reads_observed_metadata() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M04 localhost", "target_type": "url", "value": "https://localhost", "mode": "dry_run", "allowed_modules": ["m04_web_intrusion"]})
        target_id = created.json()["target"]["target_id"]
        written = client.post(f"/api/targets/{target_id}/m04/web-baseline", json={"url": "https://localhost", "status_code": 302, "headers": {"Referrer-Policy": "same-origin"}})
        read = client.get(f"/api/targets/{target_id}/m04/web-baseline")

    assert written.status_code == 200
    assert Path(written.json()["baseline_path"]).is_file()
    assert written.json()["baseline"]["observation"]["status_code"] == 302
    assert read.status_code == 200
    assert read.json()["baseline_found"] is True
