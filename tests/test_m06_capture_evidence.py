"""M06 packet-capture evidence intake tests."""

from io import BytesIO
from pathlib import Path
import struct

from fastapi.testclient import TestClient

from app.core.m06_capture_evidence import inspect_capture_header, list_m06_capture_evidence, write_m06_capture_evidence
from app.core.target_model import TARGET_IP, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(target_id="target-m06", name="M06 target", target_type=TARGET_IP, value="127.0.0.1", normalized_value="127.0.0.1", mode=TARGET_MODE_DRY_RUN, allowed_modules=["m06_mitm_network"])


def _pcap() -> bytes:
    return b"\xd4\xc3\xb2\xa1" + struct.pack("<HHIIII", 2, 4, 0, 0, 65535, 1)


def test_m06_capture_intake_records_real_pcap_metadata_without_network_activity(tmp_path: Path) -> None:
    receipt = write_m06_capture_evidence(_target(), BytesIO(_pcap()), "sample.pcap", repo_root=tmp_path)
    captures = list_m06_capture_evidence(_target(), repo_root=tmp_path)

    assert receipt["inspection"]["format"] == "pcap"
    assert receipt["inspection"]["linktype"] == 1
    assert receipt["network_capture_started_by_application"] is False
    assert Path(receipt["captured_file"]).is_file()
    assert captures[0]["sha256"] == receipt["sha256"]
    assert inspect_capture_header(b"\x0a\x0d\x0d\x0a")["format"] == "pcapng"


def test_m06_capture_api_uploads_and_lists_receipts() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M06 localhost", "target_type": "ip", "value": "127.0.0.1", "mode": "dry_run", "allowed_modules": ["m06_mitm_network"]})
        target_id = created.json()["target"]["target_id"]
        uploaded = client.post(f"/api/targets/{target_id}/m06/packet-capture", files={"capture": ("sample.pcap", _pcap(), "application/vnd.tcpdump.pcap")})
        listed = client.get(f"/api/targets/{target_id}/m06/packet-captures")

    assert uploaded.status_code == 200
    assert uploaded.json()["inspection"]["format_recognized"] is True
    assert Path(uploaded.json()["receipt_path"]).is_file()
    assert listed.status_code == 200
    assert listed.json()["capture_count"] == 1
