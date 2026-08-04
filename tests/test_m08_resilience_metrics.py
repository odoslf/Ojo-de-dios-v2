"""M08 observed resilience measurement tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m08_resilience_metrics import measurement_from_payload, read_m08_resilience_measurements, write_m08_resilience_measurements
from app.core.target_model import TARGET_URL, TARGET_MODE_CONTROLLED, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(target_id="target-m08", name="M08 target", target_type=TARGET_URL, value="https://example.com", normalized_value="https://example.com", mode=TARGET_MODE_CONTROLLED, allowed_modules=["m08_dos_resilience"])


def test_m08_measurements_persist_sample_summary_without_load_generation(tmp_path: Path) -> None:
    measurements = [
        measurement_from_payload({"observed_at": "2026-07-17T10:00:00Z", "available": True, "latency_ms": 20, "source": "monitor"}),
        measurement_from_payload({"observed_at": "2026-07-17T10:01:00Z", "available": False, "source": "monitor"}),
    ]
    path = write_m08_resilience_measurements(_target(), measurements, repo_root=tmp_path)
    report = read_m08_resilience_measurements(_target(), repo_root=tmp_path)

    assert path.is_file()
    assert report is not None
    assert report["summary"]["availability_rate"] == 0.5
    assert report["summary"]["latency_ms_average"] == 20.0
    assert report["load_generated_by_application"] is False


def test_m08_measurements_api_writes_and_reads_report() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M08 localhost", "target_type": "url", "value": "https://localhost", "mode": "controlled", "allowed_modules": ["m08_dos_resilience"]})
        target_id = created.json()["target"]["target_id"]
        written = client.post(f"/api/targets/{target_id}/m08/resilience-measurements", json={"measurements": [{"observed_at": "2026-07-17T10:00:00Z", "available": True, "latency_ms": 12, "source": "monitor"}]})
        read = client.get(f"/api/targets/{target_id}/m08/resilience-measurements")

    assert written.status_code == 200
    assert Path(written.json()["measurements_path"]).is_file()
    assert written.json()["report"]["summary"]["sample_count"] == 1
    assert read.status_code == 200
    assert read.json()["load_generated_by_application"] is False
