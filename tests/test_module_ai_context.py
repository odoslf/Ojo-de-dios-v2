"""Tests for real workspace-scoped LaIA context infrastructure for M02 through M16."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.module_context import (
    build_target_module_context_pack,
    list_target_module_ai_reviews,
    render_target_module_chatml_prompt,
    write_target_module_ai_review,
)
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.main import create_app


def _target() -> TargetRecord:
    return TargetRecord(
        target_id="target-module-context",
        name="Module Context",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
        allowed_modules=["m02_vulnerabilities"],
    )


def test_module_context_uses_only_target_module_workspace(tmp_path: Path) -> None:
    target = _target()
    pack = build_target_module_context_pack(target, "m02_vulnerabilities", repo_root=tmp_path)
    artifact = Path(str(pack["workspace_path"])) / "evidence" / "inventory.json"
    artifact.write_text('{"service":"nginx","version":"1.25"}', encoding="utf-8")

    refreshed = build_target_module_context_pack(target, "m02_vulnerabilities", repo_root=tmp_path)
    prompt = render_target_module_chatml_prompt(target, "m02_vulnerabilities", repo_root=tmp_path)
    receipt = write_target_module_ai_review(target, "m02_vulnerabilities", "mistral-local", prompt["prompt_sha256"], "{}", repo_root=tmp_path)
    reviews = list_target_module_ai_reviews(target, "m02_vulnerabilities", repo_root=tmp_path)

    assert pack["module_number"] == 2
    assert refreshed["artifact_count"] == 1
    assert refreshed["artifacts"][0]["path"] == "evidence/inventory.json"
    assert "nginx" in refreshed["artifacts"][0]["excerpt"]
    assert "<|system|>" in prompt["prompt"]
    assert receipt.is_file()
    assert "m02_vulnerabilities" in receipt.as_posix()
    assert len(reviews) == 1
    assert reviews[0]["path"] == receipt.as_posix()


def test_module_context_api_is_available_for_m02_and_rejects_m01_duplicate_flow() -> None:
    with TestClient(create_app()) as client:
        created = client.post(
            "/api/targets/create",
            json={
                "name": "Module Context Localhost",
                "target_type": "domain",
                "value": "localhost",
                "mode": "dry_run",
                "allowed_modules": ["m02_vulnerabilities"],
            },
        )
        target_id = created.json()["target"]["target_id"]
        m02_context = client.get(f"/api/targets/{target_id}/modules/m02_vulnerabilities/ai-context")
        m02_prompt = client.get(f"/api/targets/{target_id}/modules/m02_vulnerabilities/ai-prompt")
        gated_review = client.post(f"/api/targets/{target_id}/modules/m02_vulnerabilities/laia-review", json={})
        reviews = client.get(f"/api/targets/{target_id}/modules/m02_vulnerabilities/laia-reviews")
        m01_context = client.get(f"/api/targets/{target_id}/modules/m01_osint/ai-context")

    assert m02_context.status_code == 200
    assert m02_context.json()["context_pack"]["module_id"] == "m02_vulnerabilities"
    assert m02_prompt.status_code == 200
    assert len(m02_prompt.json()["chatml_prompt"]["prompt_sha256"]) == 64
    assert gated_review.status_code == 400
    assert reviews.status_code == 200
    assert reviews.json()["review_count"] == 0
    assert m01_context.status_code == 400
