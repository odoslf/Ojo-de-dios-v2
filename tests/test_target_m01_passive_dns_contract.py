"""Target-bound M01 passive DNS contract tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRequest
from app.core.target_model import TargetRecord
from app.core.target_osint import domain_for_target, list_target_passive_dns_history, run_target_passive_dns
from app.db.repositories.targets_repository import TargetsRepository
from app.db.session import create_engine_from_url, create_session_factory, init_db
from app.main import create_app


def test_target_passive_dns_writes_target_bound_m01_evidence(tmp_path: Path) -> None:
    target = TargetRequest(
        name="Localhost",
        target_type=TARGET_DOMAIN,
        value="localhost",
        mode=TARGET_MODE_DRY_RUN,
        allowed_modules=["m01_osint"],
    )
    engine = create_engine_from_url("sqlite:///:memory:")
    init_db(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        record = TargetsRepository(session).create_target(target)
        target_record = TargetRecord(
            target_id=record.target_id,
            name=record.name,
            target_type=record.target_type,
            value=record.value,
            normalized_value=record.normalized_value,
            mode=record.mode,
            allowed_modules=["m01_osint"],
        )
        result = run_target_passive_dns(target=target_record, repo_root=tmp_path)
        history = list_target_passive_dns_history(target=target_record, repo_root=tmp_path)

    assert result.module_id == "m01_osint"
    assert result.domain == "localhost"
    assert result.artifact_path.is_file()
    assert result.report_path.is_file()
    assert "storage/targets/" in result.artifact_path.as_posix()
    assert "modules/m01_osint/evidence/passive_dns/localhost.json" in result.artifact_path.as_posix()
    assert "# M01 Passive DNS Report" in result.report_path.read_text(encoding="utf-8")
    assert len(history) == 1
    assert history[0].finding_count == len(result.findings)


def test_target_m01_passive_dns_api_and_page() -> None:
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/targets/create",
            json={
                "name": "Localhost",
                "target_type": "domain",
                "value": "localhost",
                "mode": "dry_run",
                "allowed_modules": ["m01_osint"],
            },
        )
        target_id = create_response.json()["target"]["target_id"]

        api_response = client.post(f"/api/targets/{target_id}/m01/passive-dns")
        page_response = client.post(f"/targets/{target_id}/m01/passive-dns")
        history_response = client.get(f"/api/targets/{target_id}/m01/passive-dns/history")
        detail_response = client.get(f"/targets/{target_id}")
        gated_laia_page = client.post(f"/targets/{target_id}/m01/laia-review")

    assert api_response.status_code == 200
    payload = api_response.json()["m01_passive_dns"]
    assert payload["target_id"] == target_id
    assert payload["execution_scope"] == "target_bound_passive_dns_only"
    assert "exposure_notes" in payload["snapshot"]["assessment"]
    assert Path(payload["artifact_path"]).is_file()
    assert Path(payload["report_path"]).is_file()
    assert history_response.status_code == 200
    assert history_response.json()["history_count"] >= 1
    assert page_response.status_code == 200
    assert "DNS pasivo para este objetivo" in page_response.text
    assert "target_bound_passive_dns_only" in page_response.text
    assert detail_response.status_code == 200
    assert "Historial M01 guardado" in detail_response.text
    assert gated_laia_page.status_code == 200
    assert "execute_local_ai" in gated_laia_page.text
    assert "Mistral local" in gated_laia_page.text


def test_domain_for_target_rejects_non_domain_records() -> None:
    record = TargetRecord(
        target_id="t1",
        name="Email",
        target_type="email",
        value="a@example.com",
        normalized_value="a@example.com",
        mode="dry_run",
    )

    try:
        domain_for_target(record)
    except ValueError as exc:
        assert "domain and url" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported target type")
