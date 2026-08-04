import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.m01_context import (
    build_m01_target_context_pack,
    build_m01_target_prompt_envelope,
    list_m01_target_ai_reviews,
    render_m01_target_chatml_prompt,
    write_m01_target_ai_review,
)
from app.core.osint_domain_snapshot import DNSRecordSet, DomainAssessment, DomainSnapshot
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.core.target_osint import run_target_passive_dns
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(
        target_id="target-ai",
        name="AI Target",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
        allowed_modules=["m01_osint"],
    )


def _snapshot() -> DomainSnapshot:
    return DomainSnapshot(
        domain="example.com",
        addresses=("93.184.216.34",),
        canonical_name="example.com",
        status="RESOLVED",
        checked_at="2026-07-15T00:00:00+00:00",
        records=(DNSRecordSet("A", ("93.184.216.34",), "RESOLVED"),),
        assessment=DomainAssessment(
            has_ipv4=True,
            has_ipv6=False,
            has_nameservers=False,
            has_mail_exchange=False,
            has_spf=False,
            has_dmarc=False,
            exposure_notes=("IPv4 publicado",),
        ),
    )


def test_m01_target_context_pack_uses_persisted_workspace(monkeypatch, tmp_path: Path):
    target = _target()
    monkeypatch.setattr("app.core.target_osint.build_passive_domain_snapshot", lambda domain, include_external=False: _snapshot())
    run_target_passive_dns(target, repo_root=tmp_path)

    pack = build_m01_target_context_pack(target, repo_root=tmp_path).to_dict()
    envelope = build_m01_target_prompt_envelope(target, repo_root=tmp_path)
    chatml = render_m01_target_chatml_prompt(target, repo_root=tmp_path)

    assert pack["pack_type"] == "m01_target_passive_osint_context_pack"
    assert pack["history_count"] == 1
    assert pack["safety"]["target_web_request_performed"] is False
    assert envelope["external_ai_call_performed"] is False
    assert "<|system|>" in chatml["prompt"]
    assert len(chatml["prompt_sha256"]) == 64


def test_m01_target_ai_review_receipt_is_persisted(tmp_path: Path):
    target = _target()
    path = write_m01_target_ai_review(target, "mistral-local", "a" * 64, '{"summary":"ok"}', repo_root=tmp_path)
    reviews = list_m01_target_ai_reviews(target, repo_root=tmp_path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["mode"] == "m01_laia_mistral_local_review"
    assert payload["external_ai_call_performed"] is False
    assert payload["local_ai_call_performed"] is True
    assert len(reviews) == 1
    assert reviews[0].parse_status == "parsed"
    assert reviews[0].parsed_content["summary"] == "ok"
    assert reviews[0].parsed_content["confirmed_findings"] == []


def test_m01_review_parser_extracts_fenced_json(tmp_path: Path):
    target = _target()
    content = "La respuesta es:\n```json\n{\"summary\":\"listo\",\"recommended_next_steps\":[\"revisar MX\"],\"needs_more_m01_evidence\":true}\n```"
    write_m01_target_ai_review(target, "mistral-local", "b" * 64, content, repo_root=tmp_path)

    review = list_m01_target_ai_reviews(target, repo_root=tmp_path)[0]

    assert review.parse_status == "parsed"
    assert review.parsed_content["summary"] == "listo"
    assert review.parsed_content["recommended_next_steps"] == ["revisar MX"]
    assert review.parsed_content["needs_more_m01_evidence"] is True


def test_m01_ai_context_api_and_gated_review():
    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/targets/create",
            json={
                "name": "Localhost AI",
                "target_type": "domain",
                "value": "localhost",
                "mode": "dry_run",
                "allowed_modules": ["m01_osint"],
            },
        )
        target_id = create_response.json()["target"]["target_id"]
        client.post(f"/api/targets/{target_id}/m01/passive-dns")
        context_response = client.get(f"/api/targets/{target_id}/m01/ai-context")
        prompt_response = client.get(f"/api/targets/{target_id}/m01/ai-prompt")
        gated_response = client.post(f"/api/targets/{target_id}/m01/laia-review", json={})
        reviews_response = client.get(f"/api/targets/{target_id}/m01/laia-reviews")

    assert context_response.status_code == 200
    assert context_response.json()["context_pack"]["history_count"] >= 1
    assert prompt_response.status_code == 200
    assert len(prompt_response.json()["chatml_prompt"]["prompt_sha256"]) == 64
    assert gated_response.status_code == 400
    assert reviews_response.status_code == 200
    assert reviews_response.json()["review_count"] == 0
