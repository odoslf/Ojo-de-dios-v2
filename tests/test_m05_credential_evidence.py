"""M05 secret-free credential evidence tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m05_credential_evidence import (
    credential_evidence_from_payload,
    list_m05_credential_evidence,
    verify_m05_credential_material,
    write_m05_credential_evidence,
)
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(target_id="target-m05", name="M05 target", target_type=TARGET_DOMAIN, value="example.com", normalized_value="example.com", mode=TARGET_MODE_DRY_RUN, allowed_modules=["m05_credentials"])


def test_m05_receipt_never_persists_secret_material(tmp_path: Path) -> None:
    secret = "never-store-this-secret"
    evidence = credential_evidence_from_payload({"credential_type": "api_token", "label": "test token", "secret_material": secret})
    path = write_m05_credential_evidence(_target(), evidence, repo_root=tmp_path)
    receipts = list_m05_credential_evidence(_target(), repo_root=tmp_path)
    content = path.read_text(encoding="utf-8")

    assert secret not in content
    assert evidence.fingerprint_sha256 in content
    assert receipts[0]["secret_material_persisted"] is False
    assert receipts[0]["evidence"]["material_length"] == len(secret)
    verification = verify_m05_credential_material(_target(), receipts[0]["receipt_id"], secret, repo_root=tmp_path)
    mismatch = verify_m05_credential_material(_target(), receipts[0]["receipt_id"], "different-secret", repo_root=tmp_path)
    assert verification["verified"] is True
    assert mismatch["verified"] is False
    assert verification["remote_authentication_attempted"] is False
    assert secret not in Path(verification["path"]).read_text(encoding="utf-8")


def test_m05_evidence_api_persists_only_fingerprint() -> None:
    secret = "local-sensitive-value"
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M05 localhost", "target_type": "domain", "value": "localhost", "mode": "dry_run", "allowed_modules": ["m05_credentials"]})
        target_id = created.json()["target"]["target_id"]
        written = client.post(f"/api/targets/{target_id}/m05/credential-evidence", json={"credential_type": "password", "label": "local account", "secret_material": secret})
        read = client.get(f"/api/targets/{target_id}/m05/credential-evidence")
        receipt_id = Path(written.json()["receipt_path"]).stem
        verification = client.post(f"/api/targets/{target_id}/m05/credential-evidence/{receipt_id}/verify", json={"secret_material": secret})

    assert written.status_code == 200
    path = Path(written.json()["receipt_path"])
    assert path.is_file()
    assert secret not in path.read_text(encoding="utf-8")
    assert written.json()["secret_material_persisted"] is False
    assert read.status_code == 200
    assert read.json()["receipt_count"] == 1
    assert read.json()["receipts"][0]["evidence"]["credential_type"] == "password"
    assert verification.status_code == 200
    assert verification.json()["verified"] is True
    assert verification.json()["remote_authentication_attempted"] is False
