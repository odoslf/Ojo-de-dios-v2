"""M10 passive radio observation evidence tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m10_radio_observations import radio_observation_from_payload, read_m10_radio_observations, write_m10_radio_observations
from app.core.target_model import TARGET_WIFI_NETWORK, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(target_id="target-m10", name="M10 target", target_type=TARGET_WIFI_NETWORK, value="LabWiFi", normalized_value="labwifi", mode=TARGET_MODE_DRY_RUN, allowed_modules=["m10_wireless_rf"])


def test_m10_observation_persists_without_rf_activity(tmp_path: Path) -> None:
    observation = radio_observation_from_payload({"protocol": "wifi", "frequency_mhz": 2412, "label": "LabWiFi", "signal_dbm": -48, "source": "receiver_export", "observed_at": "2026-07-17T10:00:00Z"})
    path = write_m10_radio_observations(_target(), [observation], repo_root=tmp_path)
    report = read_m10_radio_observations(_target(), repo_root=tmp_path)

    assert path.is_file()
    assert report is not None
    assert report["observations"][0]["protocol"] == "wifi"
    assert report["rf_capture_started_by_application"] is False
    assert report["rf_transmission_performed"] is False


def test_m10_observations_api_writes_and_reads_report() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M10 lab", "target_type": "wifi_network", "value": "LabWiFi", "mode": "dry_run", "allowed_modules": ["m10_wireless_rf"]})
        target_id = created.json()["target"]["target_id"]
        written = client.post(f"/api/targets/{target_id}/m10/radio-observations", json={"observations": [{"protocol": "ble", "label": "Sensor", "source": "receiver_export", "observed_at": "2026-07-17T10:00:00Z"}]})
        read = client.get(f"/api/targets/{target_id}/m10/radio-observations")

    assert written.status_code == 200
    assert Path(written.json()["observations_path"]).is_file()
    assert written.json()["report"]["observation_count"] == 1
    assert read.status_code == 200
    assert read.json()["rf_transmission_performed"] is False
