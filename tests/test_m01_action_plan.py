"""Tests for evidence-derived M01 operator plans."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.m01_context import write_m01_target_ai_review
from app.core.m01_action_plan import build_m01_action_plan, write_m01_action_plan
from app.core.osint_domain_snapshot import DNSRecordSet, DomainAssessment, DomainSnapshot
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.core.target_osint import run_target_passive_dns
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(
        target_id="target-action-plan",
        name="Action Plan Target",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
        allowed_modules=["m01_osint"],
    )


def _mail_snapshot() -> DomainSnapshot:
    return DomainSnapshot(
        domain="example.com",
        addresses=("93.184.216.34",),
        canonical_name="example.com",
        status="RESOLVED",
        checked_at="2026-07-16T00:00:00+00:00",
        records=(
            DNSRecordSet("A", ("93.184.216.34",), "RESOLVED"),
            DNSRecordSet("MX", ("10 mail.example.com.",), "RESOLVED"),
            DNSRecordSet("TXT", (), "NOT_FOUND"),
        ),
        assessment=DomainAssessment(
            has_ipv4=True,
            has_ipv6=False,
            has_nameservers=True,
            has_mail_exchange=True,
            has_spf=False,
            has_dmarc=False,
            exposure_notes=("Correo publicado",),
        ),
    )


def test_action_plan_uses_persisted_findings_and_parsed_laia_review(monkeypatch, tmp_path: Path) -> None:
    target = _target()
    monkeypatch.setattr("app.core.target_osint.build_passive_domain_snapshot", lambda domain, include_external=False: _mail_snapshot())
    run_target_passive_dns(target, repo_root=tmp_path)
    write_m01_target_ai_review(
        target,
        "mistral-local",
        "a" * 64,
        '{"summary":"Revisar correo", "recommended_next_steps":["Validar los propietarios del dominio antes de cambiar DNS."]}',
        repo_root=tmp_path,
    )

    plan = build_m01_action_plan(target, repo_root=tmp_path)
    path = write_m01_action_plan(target, repo_root=tmp_path)

    assert plan.source_history_count == 1
    assert plan.source_review_count == 1
    assert {step.action_type for step in plan.steps} >= {"review_dns_mail_auth", "review_local_ai_recommendation"}
    assert all(step.to_dict()["target_activity_performed"] is False for step in plan.steps)
    assert path.is_file()
    assert '"plan_type": "m01_evidence_action_plan"' in path.read_text(encoding="utf-8")


def test_action_plan_api_and_page_write_action() -> None:
    with TestClient(create_app()) as client:
        created = client.post(
            "/api/targets/create",
            json={
                "name": "Action Plan Localhost",
                "target_type": "domain",
                "value": "localhost",
                "mode": "dry_run",
                "allowed_modules": ["m01_osint"],
            },
        )
        target_id = created.json()["target"]["target_id"]
        plan_response = client.get(f"/api/targets/{target_id}/m01/action-plan")
        write_response = client.post(f"/api/targets/{target_id}/m01/action-plan/write")
        page_response = client.post(f"/targets/{target_id}/m01/action-plan/write")

    assert plan_response.status_code == 200
    assert plan_response.json()["action_plan"]["step_count"] == 1
    assert plan_response.json()["action_plan"]["steps"][0]["action_type"] == "run_passive_dns"
    assert write_response.status_code == 200
    assert Path(write_response.json()["action_plan_path"]).is_file()
    assert page_response.status_code == 200
    assert "Plan M01 actualizado" in page_response.text
