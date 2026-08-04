"""M01 passive OSINT contract tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.osint_domain_snapshot import build_passive_domain_snapshot, normalize_domain, write_domain_snapshot
from app.main import create_app


def test_normalize_domain_rejects_urls_and_ips() -> None:
    assert normalize_domain("Example.COM.") == "example.com"
    with pytest.raises(ValueError):
        normalize_domain("https://example.com")
    with pytest.raises(ValueError):
        normalize_domain("127.0.0.1")


def test_passive_domain_snapshot_can_be_persisted_without_web_or_port_scan(tmp_path: Path) -> None:
    snapshot = build_passive_domain_snapshot("localhost")
    path = write_domain_snapshot(snapshot, repo_root=tmp_path)
    payload = path.read_text(encoding="utf-8")

    assert path.as_posix().endswith("storage/workspaces/m01_osint/passive_dns/localhost.json")
    assert '"passive_dns_only": true' in payload
    assert '"port_scan_performed": false' in payload
    assert '"web_request_performed": false' in payload
    assert '"subdomain_bruteforce_performed": false' in payload
    assert '"records"' in payload
    assert '"assessment"' in payload


def test_m01_passive_domain_snapshot_api_persists_workspace_artifact() -> None:
    artifact = Path("storage/workspaces/m01_osint/passive_dns/localhost.json")
    if artifact.exists():
        artifact.unlink()
    client = TestClient(create_app())

    response = client.post("/api/modules/m01_osint/osint/domain-snapshot", json={"domain": "localhost"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["module_id"] == "m01_osint"
    assert payload["execution_scope"] == "passive_dns_only"
    assert payload["snapshot"]["port_scan_performed"] is False
    assert payload["snapshot"]["web_request_performed"] is False
    assert payload["snapshot"]["subdomain_bruteforce_performed"] is False
    assert {record["record_type"] for record in payload["snapshot"]["records"]} >= {"A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"}
    assert "exposure_notes" in payload["snapshot"]["assessment"]
    assert artifact.is_file()
    artifact.unlink()


def test_m16_windows_start_plan_points_to_real_app_launcher_and_m01_api() -> None:
    client = TestClient(create_app())

    response = client.get("/api/ops/m16/windows-start-plan")

    assert response.status_code == 200
    payload = response.json()
    assert payload["main_windows_entrypoint"] == "scripts\\windows\\iniciar_ojo_de_dios_windows.bat"
    assert payload["m01_passive_dns_api"] == "/api/modules/m01_osint/osint/domain-snapshot"
    assert payload["m01_ready_for_passive_dns"] is True
