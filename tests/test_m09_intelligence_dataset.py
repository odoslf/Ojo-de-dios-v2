"""M09 normalized intelligence dataset tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.m09_intelligence_dataset import normalize_intelligence_record, read_m09_intelligence_dataset, write_m09_intelligence_dataset
from app.core.target_model import TARGET_SCRAPING_QUERY, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(target_id="target-m09", name="M09 target", target_type=TARGET_SCRAPING_QUERY, value="security", normalized_value="security", mode=TARGET_MODE_DRY_RUN, allowed_modules=["m09_scraping_intelligence"])


def test_m09_dataset_normalizes_and_deduplicates_without_connector_execution(tmp_path: Path) -> None:
    record = normalize_intelligence_record({"url": "https://example.com/page#part", "title": "Example", "text": "Collected text", "source": "export", "observed_at": "2026-07-17T10:00:00Z"})
    path = write_m09_intelligence_dataset(_target(), [record, record], repo_root=tmp_path)
    dataset = read_m09_intelligence_dataset(_target(), repo_root=tmp_path)

    assert path.is_file()
    assert dataset is not None
    assert dataset["input_record_count"] == 2
    assert dataset["deduplicated_record_count"] == 1
    assert dataset["records"][0]["url"] == "https://example.com/page"
    assert dataset["connector_execution_performed"] is False


def test_m09_dataset_api_persists_normalized_records() -> None:
    with TestClient(create_app()) as client:
        created = client.post("/api/targets/create", json={"name": "M09 query", "target_type": "scraping_query", "value": "security", "mode": "dry_run", "allowed_modules": ["m09_scraping_intelligence"]})
        target_id = created.json()["target"]["target_id"]
        written = client.post(f"/api/targets/{target_id}/m09/intelligence-dataset", json={"records": [{"url": "https://example.com", "title": "Example", "text": "Collected", "source": "export", "observed_at": "2026-07-17T10:00:00Z"}]})
        read = client.get(f"/api/targets/{target_id}/m09/intelligence-dataset")

    assert written.status_code == 200
    assert Path(written.json()["dataset_path"]).is_file()
    assert written.json()["dataset"]["deduplicated_record_count"] == 1
    assert read.status_code == 200
    assert read.json()["connector_execution_performed"] is False
