"""M07 authorized session metadata evidence tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m07_session_evidence import list_m07_session_evidence, session_evidence_from_payload, write_m07_session_evidence
from app.core.target_model import TARGET_IP, TARGET_MODE_CONTROLLED, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(target_id="target-m07", name="M07 target", target_type=TARGET_IP, value="127.0.0.1", normalized_value="127.0.0.1", mode=TARGET_MODE_CONTROLLED, allowed_modules=["m07_post_exploitation"])


def test_m07_session_evidence_persists_only_metadata(tmp_path: Path) -> None:
    evidence = session_evidence_from_payload({"session_reference": "case-001", "host_label": "lab-host", "platform": "windows", "privilege_level": "administrator"})
    path = write_m07_session_evidence(_target(), evidence, repo_root=tmp_path)
    entries = list_m07_session_evidence(_target(), repo_root=tmp_path)

    assert path.is_file()
    assert entries[0]["evidence"]["session_secret_persisted"] is False
    assert entries[0]["evidence"]["command_execution_performed"] is False
    assert entries[0]["evidence"]["privilege_level"] == "administrator"


def test_m07_session_evidence_api_records_no_execution() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M07 localhost", "target_type": "ip", "value": "127.0.0.1", "mode": "controlled", "allowed_modules": ["m07_post_exploitation"]})
        target_id = created.json()["target"]["target_id"]
        written = client.post(f"/api/targets/{target_id}/m07/session-evidence", json={"session_reference": "case-002", "host_label": "localhost", "platform": "linux", "state": "observed"})
        listed = client.get(f"/api/targets/{target_id}/m07/session-evidence")

    assert written.status_code == 200
    assert written.json()["command_execution_performed"] is False
    assert Path(written.json()["receipt_path"]).is_file()
    assert listed.status_code == 200
    assert listed.json()["session_count"] == 1
    assert listed.json()["network_activity_performed"] is False
