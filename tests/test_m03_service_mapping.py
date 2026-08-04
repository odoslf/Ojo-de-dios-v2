"""M03 service-map tests built from persisted M02 evidence only."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m02_vulnerability_inventory import service_observation_from_payload, write_m02_service_inventory
from app.core.m03_service_mapping import build_m03_service_map, read_m03_service_map, write_m03_service_map
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(
        target_id="target-m03",
        name="M03 target",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
        allowed_modules=["m02_vulnerabilities", "m03_network_services"],
    )


def test_m03_map_classifies_saved_m02_services_without_target_activity(tmp_path: Path) -> None:
    target = _target()
    write_m02_service_inventory(target, [service_observation_from_payload({"product": "nginx", "version": "1.25.4", "port": 443})], repo_root=tmp_path)

    service_map = build_m03_service_map(target, repo_root=tmp_path)
    path = write_m03_service_map(target, repo_root=tmp_path)
    persisted = read_m03_service_map(target, repo_root=tmp_path)

    assert service_map["source_inventory_found"] is True
    assert service_map["services"][0]["service_family"] == "web"
    assert service_map["services"][0]["target_activity_performed"] is False
    assert path.is_file()
    assert persisted is not None
    assert persisted["service_count"] == 1


def test_m03_service_map_api_uses_m02_inventory() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M03 localhost", "target_type": "domain", "value": "localhost", "mode": "dry_run", "allowed_modules": ["m02_vulnerabilities", "m03_network_services"]})
        target_id = created.json()["target"]["target_id"]
        client.post(f"/api/targets/{target_id}/m02/service-inventory", json={"services": [{"product": "OpenSSH", "version": "9.6", "port": 22}]})
        written = client.post(f"/api/targets/{target_id}/m03/service-map")
        read = client.get(f"/api/targets/{target_id}/m03/service-map")

    assert written.status_code == 200
    assert Path(written.json()["service_map_path"]).is_file()
    assert written.json()["service_map"]["services"][0]["service_family"] == "remote_access"
    assert read.status_code == 200
    assert read.json()["service_map_found"] is True
