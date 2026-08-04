"""Module catalog and M16 readiness API contract tests."""

import json
from collections.abc import Generator
from pathlib import Path
from shutil import rmtree

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.hermes_assist import HermesAssistRequest, HermesAssistResponse
from app.ai.hermes_receipts import write_hermes_assist_receipt
from app.api.routes_modules import get_hermes_assist_service, get_local_mistral_client
from app.config import Settings
from app.db.session import get_session, init_db
from app.main import create_app


class _FakeHermesAssistService:
    def __init__(self) -> None:
        self.settings = Settings(_env_file=None, ai_enabled=True, angel_enabled=True, deepseek_api_key="secret")
        self.requests = []

    def ask_json(self, request):
        self.requests.append(request)
        return HermesAssistResponse(
            model=request.model,
            content='{"answer":"ok","execution_implied":false}',
            raw={"id": "hermes-api-test"},
        )


class _FakeMistralClient:
    model = "CognitiveComputations/dolphin-mistral-nemo:12b"

    def __init__(self) -> None:
        self.prompts = []

    def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return '{"summary":"ok token=abc123","execution_implied":false}'


def test_modules_api_lists_official_and_reserved_modules() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules")

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 20
    assert payload["modules"][0]["module_id"] == "m01_osint"
    assert payload["modules"][-1]["module_id"] == "m20_future_expansion"
    assert payload["modules"][-1]["reserved"] is True


def test_modules_api_can_hide_reserved_modules() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules", params={"include_reserved": False})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 16
    assert all(module["official"] is True for module in payload["modules"])


def test_modules_api_returns_single_module_and_404_for_unknown() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m16_ops_quality")
    missing = client.get("/api/modules/m99_unknown")

    assert response.status_code == 200
    assert response.json()["module"]["module_number"] == 16
    assert response.json()["module"]["workspace_path"] == "storage/workspaces/m16_ops_quality"
    assert missing.status_code == 404



def test_modules_api_returns_documentation_backed_techniques() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m07_post_exploitation/techniques")
    summary = client.get("/api/modules/techniques/summary")
    missing = client.get("/api/modules/m99_unknown/techniques")

    assert response.status_code == 200
    assert summary.status_code == 200
    assert missing.status_code == 404
    payload = response.json()
    assert payload["execution_implied"] is False
    assert payload["count"] > 0
    first_ids = {item["technique_id"] for item in payload["techniques"]}
    assert "post.c2.havoc_deploy" in first_ids
    assert summary.json()["summary"]["module_counts"]["m07_post_exploitation"] == payload["count"]


def test_modules_api_bootstraps_technique_workspace() -> None:
    workspace_path = Path("storage/workspaces/m07_post_exploitation/techniques/post.c2.havoc_deploy")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    before = client.get("/api/modules/m07_post_exploitation/techniques/post.c2.havoc_deploy/workspace")
    response = client.post(
        "/api/modules/m07_post_exploitation/techniques/post.c2.havoc_deploy/workspace/bootstrap"
    )
    after = client.get("/api/modules/m07_post_exploitation/techniques/post.c2.havoc_deploy/workspace")
    missing = client.post("/api/modules/m07_post_exploitation/techniques/missing.tech/workspace/bootstrap")
    missing_read = client.get("/api/modules/m07_post_exploitation/techniques/missing.tech/workspace")

    assert before.status_code == 200
    assert response.status_code == 200
    assert after.status_code == 200
    assert missing.status_code == 404
    assert missing_read.status_code == 404
    assert before.json()["exists"] is False
    payload = response.json()
    state = after.json()
    assert payload["execution_implied"] is False
    assert payload["workspace"]["technique_id"] == "post.c2.havoc_deploy"
    assert state["manifest_exists"] is True
    assert state["manifest"]["source_technique_id"] == "post.c2.havoc_deploy"
    write_artifact = client.post(
        "/api/modules/m07_post_exploitation/techniques/post.c2.havoc_deploy/workspace/artifacts",
        json={
            "artifact_name": "operator-plan",
            "artifact_type": "input",
            "payload": {"scope": "lab", "execute": False},
        },
    )
    list_artifacts = client.get(
        "/api/modules/m07_post_exploitation/techniques/post.c2.havoc_deploy/workspace/artifacts"
    )
    read_artifact = client.get(
        "/api/modules/m07_post_exploitation/techniques/post.c2.havoc_deploy/workspace/artifacts/operator-plan",
        params={"artifact_type": "input"},
    )
    assert write_artifact.status_code == 200
    assert list_artifacts.status_code == 200
    assert read_artifact.status_code == 200
    assert write_artifact.json()["execution_implied"] is False
    assert list_artifacts.json()["count"] == 1
    assert read_artifact.json()["payload"] == {"execute": False, "scope": "lab"}
    assert Path(payload["workspace"]["manifest_path"]).is_file()
    rmtree(workspace_path)


def test_modules_api_bootstraps_all_module_technique_workspaces_with_confirmation() -> None:
    workspace_root = Path("storage/workspaces/m07_post_exploitation/techniques")
    if workspace_root.exists():
        rmtree(workspace_root)
    client = TestClient(create_app())

    blocked = client.post("/api/modules/m07_post_exploitation/techniques/workspaces/bootstrap", json={})
    response = client.post(
        "/api/modules/m07_post_exploitation/techniques/workspaces/bootstrap",
        json={"execute_bootstrap": True},
    )

    assert blocked.status_code == 400
    assert blocked.json()["detail"] == "Technique workspace bootstrap requires execute_bootstrap=true."
    assert response.status_code == 200
    payload = response.json()
    assert payload["module_id"] == "m07_post_exploitation"
    assert payload["workspace_count"] >= 1
    assert payload["execution_implied"] is False
    assert all(Path(workspace["manifest_path"]).is_file() for workspace in payload["workspaces"])
    rmtree(workspace_root)


def test_modules_api_returns_validated_manifest() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m17_hackrf_sdr/manifest")

    assert response.status_code == 200
    manifest = response.json()["manifest"]
    assert manifest["module_id"] == "m17_hackrf_sdr"
    assert manifest["reserved"] is True
    assert manifest["doc_path"] is None


def test_m16_readiness_api_returns_honest_partial_status_without_writing() -> None:
    runtime_path = Path("storage/runtime/m16_readiness_status.json")
    if runtime_path.exists():
        runtime_path.unlink()
    client = TestClient(create_app())

    response = client.get("/api/ops/m16/readiness")

    assert response.status_code == 200
    readiness = response.json()["readiness"]
    assert readiness["module_id"] == "m16_ops_quality"
    assert readiness["status"] in {"PARTIAL", "READY_CONTROLLED", "FAILED"}
    assert not runtime_path.exists()


def test_m16_readiness_write_api_persists_runtime_status_without_secret_value() -> None:
    runtime_path = Path("storage/runtime/m16_readiness_status.json")
    if runtime_path.exists():
        runtime_path.unlink()
    client = TestClient(create_app())

    response = client.post("/api/ops/m16/readiness/write")

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_status_path"] == "storage/runtime/m16_readiness_status.json"
    assert runtime_path.is_file()
    assert "DEEPSEEK_API_KEY" not in runtime_path.read_text(encoding="utf-8")
    runtime_path.unlink()


def test_knowledge_build_api_requires_explicit_confirmation() -> None:
    client = TestClient(create_app())

    response = client.post("/api/ops/knowledge/build", json={"mode": "docs-only"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Knowledge build requires execute_build=true."


def test_knowledge_build_and_search_api_use_local_artifacts_without_external_calls() -> None:
    knowledge_dir = Path("storage/knowledge")
    generated_files = (
        knowledge_dir / "source_manifest.json",
        knowledge_dir / "chunks.jsonl",
        knowledge_dir / "keyword_index.json",
        knowledge_dir / "knowledge_status.json",
    )
    for path in generated_files:
        if path.exists():
            path.unlink()
    client = TestClient(create_app())

    build_response = client.post("/api/ops/knowledge/build", json={"execute_build": True, "mode": "docs-only"})
    status_response = client.get("/api/ops/knowledge/status")
    search_response = client.get("/api/ops/knowledge/search", params={"q": "Hermes Agent", "limit": 3})

    assert build_response.status_code == 200
    build_payload = build_response.json()
    assert build_payload["external_api_call_performed"] is False
    assert build_payload["model_download_performed"] is False
    assert build_payload["knowledge_status"]["status"] == "READY_DOCS_ONLY"
    assert status_response.status_code == 200
    assert status_response.json()["knowledge_status"]["status"] == "READY_DOCS_ONLY"
    assert search_response.status_code == 200
    search_payload = search_response.json()["search"]
    assert search_payload["knowledge_status"] == "READY_DOCS_ONLY"
    assert search_payload["count"] >= 1
    for path in generated_files:
        if path.exists():
            path.unlink()


def test_knowledge_context_pack_api_and_hermes_preview_inject_local_context() -> None:
    knowledge_dir = Path("storage/knowledge")
    generated_files = (
        knowledge_dir / "source_manifest.json",
        knowledge_dir / "chunks.jsonl",
        knowledge_dir / "keyword_index.json",
        knowledge_dir / "knowledge_status.json",
    )
    for path in generated_files:
        if path.exists():
            path.unlink()
    client = TestClient(create_app())
    build_response = client.post("/api/ops/knowledge/build", json={"execute_build": True, "mode": "docs-only"})
    assert build_response.status_code == 200

    context_response = client.get("/api/ops/knowledge/context-pack", params={"q": "Hermes Agent", "limit": 2})
    preview_response = client.post(
        "/api/ai/hermes/assist/request-preview",
        json={
            "question": "Prepare Hermes Agent context?",
            "context": {"module_id": "m16_ops_quality"},
            "use_knowledge_base": True,
            "knowledge_query": "Hermes Agent",
            "knowledge_limit": 2,
        },
    )

    assert context_response.status_code == 200
    context_pack = context_response.json()["context_pack"]
    assert context_pack["mode"] == "local_knowledge_search_no_ai"
    assert context_pack["external_ai_call_performed"] is False
    assert context_pack["result_count"] >= 1
    assert preview_response.status_code == 200
    user_payload = json.loads(preview_response.json()["deepseek_request"]["messages"][1]["content"])
    context_payload = json.loads(user_payload["context_json"])
    assert context_payload["module_id"] == "m16_ops_quality"
    assert context_payload["local_knowledge_context"]["pack_type"] == "knowledge_search_context_pack"
    assert context_payload["local_knowledge_context"]["external_ai_call_performed"] is False
    for path in generated_files:
        if path.exists():
            path.unlink()


def test_toolhealth_python_runtime_api_reports_ready_runtime() -> None:
    client = TestClient(create_app())

    response = client.get("/api/ops/toolhealth/python-runtime")

    assert response.status_code == 200
    payload = response.json()["tool_health"]
    assert payload["tool_id"] == "python.runtime"
    assert payload["module_id"] == "m16_ops_quality"
    assert payload["status"] == "READY_CONTROLLED"


def test_hermes_assist_request_preview_api_builds_deepseek_payload_without_call() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/ai/hermes/assist/request-preview",
        json={
            "question": "Prepare a safe parser review?",
            "context": {"module_id": "m16_ops_quality", "round": 16},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "hermes_deepseek_request_preview_no_external_call"
    assert payload["external_ai_call_performed"] is False
    assert payload["deepseek_request"]["model"] == "deepseek-v4-pro"
    assert payload["deepseek_request"]["response_format"] == {"type": "json_object"}
    assert payload["deepseek_request"]["thinking"] == {"type": "disabled"}
    assert "Do not execute tools" in payload["deepseek_request"]["messages"][0]["content"]
    user_payload = json.loads(payload["deepseek_request"]["messages"][1]["content"])
    context_payload = json.loads(user_payload["context_json"])
    assert context_payload["module_id"] == "m16_ops_quality"
    assert user_payload["required_output"]["execution_implied"] is False


def test_hermes_assist_request_preview_rejects_bad_context_and_unapproved_pro() -> None:
    client = TestClient(create_app())

    bad_context = client.post(
        "/api/ai/hermes/assist/request-preview",
        json={"question": "x", "context": ["bad"]},
    )
    pro_model = client.post(
        "/api/ai/hermes/assist/request-preview",
        json={"question": "x", "context": {}, "model": "deepseek-v4-pro"},
    )
    approved_pro_model = client.post(
        "/api/ai/hermes/assist/request-preview",
        json={
            "question": "x",
            "context": {},
            "model": "deepseek-v4-pro",
            "allow_pro_model": True,
        },
    )

    assert bad_context.status_code == 400
    assert bad_context.json()["detail"] == "Hermes context must be a JSON object."
    assert pro_model.status_code == 200
    assert pro_model.json()["deepseek_request"]["model"] == "deepseek-v4-pro"
    assert approved_pro_model.status_code == 200
    assert approved_pro_model.json()["deepseek_request"]["model"] == "deepseek-v4-pro"


def test_hermes_assist_api_requires_explicit_external_ai_approval() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/ai/hermes/assist",
        json={"question": "Can Hermes help?", "context": {"module_id": "m16_ops_quality"}},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Hermes assist requires execute_external_ai=true."


def test_hermes_assist_api_returns_503_when_runtime_ai_is_not_configured() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/ai/hermes/assist",
        json={
            "execute_external_ai": True,
            "question": "Can Hermes help?",
            "context": {"module_id": "m16_ops_quality"},
        },
    )

    assert response.status_code == 503
    assert "disabled or missing DEEPSEEK_API_KEY" in response.json()["detail"]


def test_hermes_assist_api_calls_injected_service_after_approval() -> None:
    app = create_app()
    service = _FakeHermesAssistService()
    app.dependency_overrides[get_hermes_assist_service] = lambda: service
    client = TestClient(app)

    response = client.post(
        "/api/ai/hermes/assist",
        json={
            "execute_external_ai": True,
            "question": "Review this plan safely.",
            "context": {"module_id": "m16_ops_quality", "round": 17},
        },
    )

    assert response.status_code == 200
    body = response.json()
    payload = body["hermes_assist"]
    receipt = body["receipt"]
    receipt_path = Path(receipt["path"])
    assert payload["mode"] == "deepseek_json_assist_no_execution"
    assert payload["external_ai_call_performed"] is True
    assert payload["content"] == '{"answer":"ok","execution_implied":false}'
    assert receipt_path.is_file()
    assert receipt["payload"]["request"]["context"]["round"] == 17
    assert receipt["payload"]["external_ai_call_performed"] is True
    assert len(service.requests) == 1
    assert service.requests[0].context["round"] == 17
    receipt_path.unlink()


def test_hermes_assist_receipts_api_lists_reads_and_404s_redacted_receipts() -> None:
    receipt = write_hermes_assist_receipt(
        HermesAssistRequest(
            question="Review without leaking token=abc123",
            context={"module_id": "m16_ops_quality", "api_key": "secret-value"},
        ),
        HermesAssistResponse(
            model="deepseek-v4-flash",
            content='{"answer":"ok","password":"abc123"}',
            raw={"id": "receipt-api-test", "authorization": "Bearer secret"},
        ),
        receipt_id="receipt-api-test",
    )
    client = TestClient(create_app())

    list_response = client.get("/api/ai/hermes/assist/receipts")
    summary_response = client.get("/api/ai/hermes/assist/receipts/summary")
    context_response = client.get("/api/ai/hermes/assist/receipts/receipt-api-test/context-pack")
    envelope_response = client.get("/api/ai/hermes/assist/receipts/receipt-api-test/prompt-envelope")
    chatml_response = client.get("/api/ai/hermes/assist/receipts/receipt-api-test/chatml-prompt")
    blocked_review_response = client.post("/api/ai/hermes/assist/receipts/receipt-api-test/laia-review", json={})
    read_response = client.get("/api/ai/hermes/assist/receipts/receipt-api-test")
    missing_response = client.get("/api/ai/hermes/assist/receipts/missing-receipt")

    assert list_response.status_code == 200
    assert summary_response.status_code == 200
    assert context_response.status_code == 200
    assert envelope_response.status_code == 200
    assert chatml_response.status_code == 200
    assert blocked_review_response.status_code == 400
    assert read_response.status_code == 200
    assert missing_response.status_code == 404
    assert any(item["receipt_id"] == "receipt-api-test" for item in list_response.json()["receipts"])
    assert summary_response.json()["summary"]["models"]["deepseek-v4-pro"] >= 1
    context_pack = context_response.json()["context_pack"]
    assert context_pack["mode"] == "hermes_receipt_context_no_external_call"
    assert context_pack["external_ai_call_performed"] is False
    assert len(context_pack["payload_checksum"]) == 64
    envelope = envelope_response.json()["prompt_envelope"]
    assert envelope["mode"] == "hermes_receipt_prompt_envelope_no_external_call"
    assert envelope["response_schema"]["properties"]["execution_implied"]["const"] is False
    chatml = chatml_response.json()["chatml_prompt"]
    assert chatml["mode"] == "hermes_receipt_chatml_prompt_no_external_call"
    assert chatml["prompt"].startswith("<|im_start|>system")
    assert len(chatml["prompt_sha256"]) == 64
    fake_mistral = _FakeMistralClient()
    app = create_app()
    app.dependency_overrides[get_local_mistral_client] = lambda: fake_mistral
    review_response = TestClient(app).post(
        "/api/ai/hermes/assist/receipts/receipt-api-test/laia-review",
        json={"execute_local_ai": True},
    )
    assert review_response.status_code == 200
    review_payload = review_response.json()
    assert review_payload["local_ai_call_performed"] is True
    assert "abc123" not in review_payload["content"]
    review_receipt_path = Path(review_payload["review_receipt"]["path"])
    assert review_receipt_path.is_file()
    assert "abc123" not in review_receipt_path.read_text(encoding="utf-8")
    assert fake_mistral.prompts[0].startswith("<|im_start|>system")
    review_id = review_payload["review_receipt"]["receipt_id"]
    blocked_audit_response = client.post(f"/api/ai/hermes/assist/laia-reviews/{review_id}/audit", json={})
    audit_response = TestClient(app).post(
        f"/api/ai/hermes/assist/laia-reviews/{review_id}/audit",
        json={"execute_local_ai": True},
    )
    missing_audit_response = client.post(
        "/api/ai/hermes/assist/laia-reviews/missing-review/audit",
        json={"execute_local_ai": True},
    )
    reviews_response = client.get("/api/ai/hermes/assist/receipts/receipt-api-test/laia-reviews")
    reviews_summary_response = client.get(
        "/api/ai/hermes/assist/laia-reviews/summary",
        params={"source_receipt_id": "receipt-api-test"},
    )
    read_review_response = client.get(f"/api/ai/hermes/assist/laia-reviews/{review_id}")
    review_context_response = client.get(f"/api/ai/hermes/assist/laia-reviews/{review_id}/context-pack")
    review_envelope_response = client.get(f"/api/ai/hermes/assist/laia-reviews/{review_id}/prompt-envelope")
    review_chatml_response = client.get(f"/api/ai/hermes/assist/laia-reviews/{review_id}/chatml-prompt")
    missing_review_response = client.get("/api/ai/hermes/assist/laia-reviews/missing-review")
    missing_context_response = client.get("/api/ai/hermes/assist/laia-reviews/missing-review/context-pack")
    missing_envelope_response = client.get("/api/ai/hermes/assist/laia-reviews/missing-review/prompt-envelope")
    missing_chatml_response = client.get("/api/ai/hermes/assist/laia-reviews/missing-review/chatml-prompt")
    assert reviews_response.status_code == 200
    assert reviews_summary_response.status_code == 200
    assert read_review_response.status_code == 200
    assert review_context_response.status_code == 200
    assert review_envelope_response.status_code == 200
    assert review_chatml_response.status_code == 200
    assert blocked_audit_response.status_code == 400
    assert audit_response.status_code == 200
    assert missing_audit_response.status_code == 404
    assert missing_review_response.status_code == 404
    assert missing_context_response.status_code == 404
    assert missing_envelope_response.status_code == 404
    assert missing_chatml_response.status_code == 404
    assert reviews_response.json()["count"] >= 1
    review_summary = reviews_summary_response.json()["summary"]
    assert review_summary["source_receipt_id"] == "receipt-api-test"
    assert review_summary["local_ai_call_count"] >= 1
    assert review_summary["models"][fake_mistral.model] >= 1
    context_pack = review_context_response.json()["context_pack"]
    assert context_pack["mode"] == "laia_receipt_review_context_no_ai_call"
    assert context_pack["review_id"] == review_id
    assert context_pack["source_receipt_id"] == "receipt-api-test"
    assert context_pack["source_local_ai_call_performed"] is True
    assert len(context_pack["payload_checksum"]) == 64
    review_envelope = review_envelope_response.json()["prompt_envelope"]
    assert review_envelope["mode"] == "laia_receipt_review_prompt_envelope_no_ai_call"
    assert review_envelope["user_context"]["review_id"] == review_id
    assert review_envelope["response_schema"]["properties"]["execution_implied"]["const"] is False
    review_chatml = review_chatml_response.json()["chatml_prompt"]
    assert review_chatml["mode"] == "laia_receipt_review_chatml_prompt_no_ai_call"
    assert review_chatml["prompt"].startswith("<|im_start|>system")
    assert review_chatml["review_id"] == review_id
    assert len(review_chatml["prompt_sha256"]) == 64
    audit_payload = audit_response.json()
    assert audit_payload["mode"] == "laia_mistral_review_receipt_audit"
    assert audit_payload["local_ai_call_performed"] is True
    assert audit_payload["review_id"] == review_id
    assert audit_payload["source_receipt_id"] == "receipt-api-test"
    assert "abc123" not in audit_payload["content"]
    audit_receipt_path = Path(audit_payload["audit_receipt"]["path"])
    assert audit_receipt_path.is_file()
    assert audit_payload["audit_receipt"]["payload"]["source_review_id"] == review_id
    assert "abc123" not in audit_receipt_path.read_text(encoding="utf-8")
    assert fake_mistral.prompts[1].startswith("<|im_start|>system")
    assert read_review_response.json()["review"]["payload"]["source_receipt_id"] == "receipt-api-test"
    audit_receipt_path.unlink()
    review_receipt_path.unlink()
    payload = read_response.json()["receipt"]["payload"]
    assert payload["request"]["context"]["api_key"] == "<redacted>"
    assert payload["request"]["question"] == "Review without leaking token=<redacted>"
    assert payload["response"]["raw"]["authorization"] == "<redacted>"
    assert "abc123" not in receipt.path.read_text(encoding="utf-8")
    receipt.path.unlink()


def test_ai_module_context_pack_api_returns_bounded_context() -> None:
    client = TestClient(create_app())

    response = client.get("/api/ai/modules/context-pack", params={"include_reserved": False})

    assert response.status_code == 200
    context_pack = response.json()["context_pack"]
    assert context_pack["module_count"] == 16
    assert context_pack["mode"] == "metadata_only_no_execution"
    assert context_pack["ai_settings"]["deepseek_api_key"] in {"missing", "set"}


def test_ai_module_explanation_api_returns_reserved_contract_and_404() -> None:
    client = TestClient(create_app())

    response = client.get("/api/ai/modules/m17_hackrf_sdr/explain")
    missing = client.get("/api/ai/modules/m99_unknown/explain")

    assert response.status_code == 200
    explanation = response.json()["module_explanation"]
    assert explanation["module_id"] == "m17_hackrf_sdr"
    assert explanation["next_user_required"] is True
    assert explanation["execution_implied"] is False
    assert missing.status_code == 404


def test_ai_tool_install_context_pack_api_returns_bounded_context() -> None:
    client = TestClient(create_app())

    response = client.get("/api/ai/modules/m01_osint/install/context-pack")
    missing = client.get("/api/ai/modules/m99_unknown/install/context-pack")

    assert response.status_code == 200
    context = response.json()["context_pack"]
    assert context["module_id"] == "m01_osint"
    assert context["mode"] == "install_metadata_only_no_execution"
    assert context["external_ai_call_performed"] is False
    assert context["plan"]["execution_performed"] is False
    assert len(context["checksum"]) == 64
    assert missing.status_code == 404


def test_ai_module_prompt_envelope_api_is_prompt_ready_without_llm_call() -> None:
    client = TestClient(create_app())

    response = client.get("/api/ai/modules/m16_ops_quality/prompt-envelope")
    missing = client.get("/api/ai/modules/m99_unknown/prompt-envelope")

    assert response.status_code == 200
    envelope = response.json()["prompt_envelope"]
    assert envelope["requested_module_id"] == "m16_ops_quality"
    assert envelope["external_ai_call_performed"] is False
    assert envelope["response_schema"]["properties"]["execution_implied"]["const"] is False
    assert missing.status_code == 404


def test_module_documented_tools_api_returns_docs_backed_inventory() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m01_osint/documented-tools")
    missing = client.get("/api/modules/m99_unknown/documented-tools")

    assert response.status_code == 200
    payload = response.json()
    tool_ids = {tool["tool_id"] for tool in payload["tools"]}
    assert payload["module_id"] == "m01_osint"
    assert payload["count"] >= 20
    assert payload["execution_implied"] is False
    assert "nmap" in tool_ids
    assert "have-i-been-pwned" in tool_ids
    assert missing.status_code == 404


def test_module_tool_definitions_api_returns_validated_definitions() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m01_osint/tool-definitions")
    missing = client.get("/api/modules/m99_unknown/tool-definitions")

    assert response.status_code == 200
    payload = response.json()
    definitions = {definition["tool_id"]: definition for definition in payload["tool_definitions"]}
    assert payload["module_id"] == "m01_osint"
    assert payload["count"] >= 20
    assert payload["execution_implied"] is False
    assert definitions["nmap"]["approval_policy"] == "approval_required"
    assert definitions["nmap"]["execution_implied"] is False
    assert definitions["nmap"]["metadata"]["source_path"] == "docs/MODULE_TOOL_INVENTORY.md"
    assert missing.status_code == 404


def test_module_tool_registry_api_returns_module_scoped_registry() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m01_osint/tool-registry")
    missing = client.get("/api/modules/m99_unknown/tool-registry")

    assert response.status_code == 200
    payload = response.json()
    assert payload["module_id"] == "m01_osint"
    assert payload["count"] >= 20
    assert payload["execution_implied"] is False
    assert "m01_osint/nmap" in payload["registry_keys"]
    assert all(definition["module_ids"] == ["m01_osint"] for definition in payload["tool_definitions"])
    assert missing.status_code == 404


def test_module_install_plan_api_returns_reviewable_non_executing_plan() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m01_osint/install-plan")
    missing = client.get("/api/modules/m99_unknown/install-plan")

    assert response.status_code == 200
    plan = response.json()["install_plan"]
    assert plan["module_id"] == "m01_osint"
    assert plan["count"] >= 20
    assert plan["execution_performed"] is False
    assert plan["needs_metadata_count"] >= 1
    assert all(step["execution_performed"] is False for step in plan["steps"])
    assert missing.status_code == 404


def test_module_install_plan_prepare_api_persists_and_reads_workspace_plan() -> None:
    workspace_path = Path("storage/workspaces/m01_osint")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    missing_before = client.get("/api/modules/m01_osint/install-plan/prepared")
    prepare_response = client.post("/api/modules/m01_osint/install-plan/prepare")
    read_response = client.get("/api/modules/m01_osint/install-plan/prepared")

    assert missing_before.status_code == 404
    assert prepare_response.status_code == 200
    assert read_response.status_code == 200
    prepared = prepare_response.json()["prepared_install_plan"]
    payload = read_response.json()["payload"]
    assert prepared["module_id"] == "m01_osint"
    assert prepared["execution_performed"] is False
    assert Path(prepared["path"]).is_file()
    assert payload["approval_required_before_execution"] is True
    assert payload["install_plan"]["execution_performed"] is False
    rmtree(workspace_path)


def test_module_install_receipts_api_lists_empty_workspace_receipts() -> None:
    workspace_path = Path("storage/workspaces/m16_ops_quality")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    response = client.get("/api/modules/m16_ops_quality/install-receipts")
    missing = client.get("/api/modules/m99_unknown/install-receipts")
    missing_receipt = client.get("/api/modules/m16_ops_quality/install-receipts/missing")

    assert response.status_code == 200
    assert response.json()["module_id"] == "m16_ops_quality"
    assert response.json()["install_receipts"] == []
    assert response.json()["count"] == 0
    assert missing.status_code == 404
    assert missing_receipt.status_code == 404


def test_module_version_lock_candidates_api_returns_non_persisted_candidates() -> None:
    client = TestClient(create_app())

    response = client.get("/api/modules/m01_osint/version-locks/candidates")
    missing = client.get("/api/modules/m99_unknown/version-locks/candidates")

    assert response.status_code == 200
    payload = response.json()
    candidates = {candidate["tool_id"]: candidate for candidate in payload["version_lock_candidates"]}
    assert payload["module_id"] == "m01_osint"
    assert payload["count"] >= 20
    assert payload["persisted"] is False
    assert candidates["m01_osint/nmap"]["status"] == "NEEDS_REVIEW"
    assert candidates["m01_osint/nmap"]["recommended_version"] == "unresolved"
    assert missing.status_code == 404


def test_module_version_lock_bootstrap_api_persists_candidates_in_request_db() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    init_db(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def override_get_session() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)

    response = client.post("/api/modules/m01_osint/version-locks/bootstrap")

    assert response.status_code == 200
    payload = response.json()
    locks = {lock["tool_id"]: lock for lock in payload["version_locks"]}
    assert payload["module_id"] == "m01_osint"
    assert payload["count"] >= 20
    assert payload["persisted"] is True
    assert locks["m01_osint/nmap"]["status"] == "NEEDS_REVIEW"
    assert locks["m01_osint/nmap"]["module_id"] == "m01_osint"


def test_module_workspace_bootstrap_api_creates_workspace_structure() -> None:
    workspace_path = Path("storage/workspaces/m01_osint")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    response = client.post("/api/modules/m01_osint/workspace/bootstrap", params={"include_documented_tools": True})

    assert response.status_code == 200
    bootstrap = response.json()["bootstrap"]
    tool_ids = {workspace["tool_id"] for workspace in bootstrap["tool_workspaces"]}
    assert bootstrap["module_id"] == "m01_osint"
    assert bootstrap["documented_tool_count"] >= 20
    assert bootstrap["created_tool_workspace_count"] == bootstrap["documented_tool_count"]
    assert "nmap" in tool_ids
    assert (workspace_path / "workspace_manifest.json").is_file()
    assert (workspace_path / "tools" / "nmap" / "tool_workspace_manifest.json").is_file()
    rmtree(workspace_path)


def test_module_tool_run_api_prepares_named_run_workspace() -> None:
    workspace_path = Path("storage/workspaces/m02_vulnerabilities")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    response = client.post(
        "/api/modules/m02_vulnerabilities/tool-runs",
        params={"tool_id": "Nuclei", "run_id": "api-smoke"},
    )

    assert response.status_code == 200
    run_workspace = response.json()["tool_run_workspace"]
    assert run_workspace["module_id"] == "m02_vulnerabilities"
    assert run_workspace["tool_id"] == "nuclei"
    assert run_workspace["run_id"] == "api-smoke"
    assert (workspace_path / "tools" / "nuclei" / "tool_runs" / "api-smoke" / "tool_run_manifest.json").is_file()
    rmtree(workspace_path)


def test_module_workspace_state_api_reports_created_tools_and_runs() -> None:
    workspace_path = Path("storage/workspaces/m03_network_services")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    bootstrap_response = client.post(
        "/api/modules/m03_network_services/workspace/bootstrap",
        params={"include_documented_tools": True},
    )
    run_response = client.post(
        "/api/modules/m03_network_services/tool-runs",
        params={"tool_id": "Hydra", "run_id": "api-state"},
    )
    artifact_response = client.post(
        "/api/modules/m03_network_services/tool-runs/api-state/inputs",
        params={"tool_id": "Hydra", "artifact_name": "target-host"},
        json={"host": "192.0.2.20"},
    )
    lifecycle_response = client.patch(
        "/api/modules/m03_network_services/tool-runs/api-state/status",
        params={"tool_id": "Hydra", "status": "running"},
    )
    state_response = client.get("/api/modules/m03_network_services/workspace/state")

    assert bootstrap_response.status_code == 200
    assert run_response.status_code == 200
    assert artifact_response.status_code == 200
    assert lifecycle_response.status_code == 200
    assert state_response.status_code == 200
    state = state_response.json()["workspace_state"]
    tools = {tool["tool_id"]: tool for tool in state["tools"]}
    assert state["workspace_exists"] is True
    assert state["manifest_exists"] is True
    assert state["tool_count"] >= 1
    assert state["run_count"] == 1
    hydra_run = tools["hydra"]["runs"][0]
    assert hydra_run["run_id"] == "api-state"
    assert hydra_run["status"] == "running"
    assert hydra_run["artifact_count"] == 1
    assert hydra_run["total_artifact_bytes"] > 0
    rmtree(workspace_path)


def test_module_tool_run_input_api_writes_json_artifact() -> None:
    workspace_path = Path("storage/workspaces/m04_web_intrusion")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    run_response = client.post(
        "/api/modules/m04_web_intrusion/tool-runs",
        params={"tool_id": "ffuf", "run_id": "input-api"},
    )
    artifact_response = client.post(
        "/api/modules/m04_web_intrusion/tool-runs/input-api/inputs",
        params={"tool_id": "ffuf", "artifact_name": "target-url"},
        json={"url": "https://example.test", "wordlist": "internal-small"},
    )

    assert run_response.status_code == 200
    assert artifact_response.status_code == 200
    artifact = artifact_response.json()["artifact"]
    artifact_path = Path(artifact["path"])
    assert artifact["artifact_name"] == "target-url"
    assert artifact["content_type"] == "application/json"
    assert len(artifact["sha256"]) == 64
    assert artifact_path.is_file()
    assert '"url": "https://example.test"' in artifact_path.read_text(encoding="utf-8")
    rmtree(workspace_path)


def test_module_tool_run_artifacts_api_writes_and_lists_artifacts() -> None:
    workspace_path = Path("storage/workspaces/m05_credentials")
    if workspace_path.exists():
        rmtree(workspace_path)
    client = TestClient(create_app())

    run_response = client.post(
        "/api/modules/m05_credentials/tool-runs",
        params={"tool_id": "Hashcat", "run_id": "artifact-api"},
    )
    output_response = client.post(
        "/api/modules/m05_credentials/tool-runs/artifact-api/artifacts",
        params={"tool_id": "Hashcat", "artifact_name": "candidate-summary", "artifact_type": "output"},
        json={"candidates": []},
    )
    list_response = client.get(
        "/api/modules/m05_credentials/tool-runs/artifact-api/artifacts",
        params={"tool_id": "Hashcat"},
    )
    read_response = client.get(
        "/api/modules/m05_credentials/tool-runs/artifact-api/artifacts/candidate-summary",
        params={"tool_id": "Hashcat", "artifact_type": "output"},
    )
    lifecycle_response = client.patch(
        "/api/modules/m05_credentials/tool-runs/artifact-api/status",
        params={"tool_id": "Hashcat", "status": "completed", "note": "candidate summary reviewed"},
    )
    summary_response = client.get(
        "/api/modules/m05_credentials/tool-runs/artifact-api",
        params={"tool_id": "Hashcat"},
    )
    ai_context_response = client.get(
        "/api/ai/modules/m05_credentials/tool-runs/artifact-api/context-pack",
        params={"tool_id": "Hashcat"},
    )

    assert run_response.status_code == 200
    assert output_response.status_code == 200
    assert list_response.status_code == 200
    assert read_response.status_code == 200
    assert lifecycle_response.status_code == 200
    assert summary_response.status_code == 200
    assert ai_context_response.status_code == 200
    artifacts = list_response.json()["artifacts"]
    assert len(artifacts) == 1
    assert artifacts[0]["artifact_name"] == "candidate-summary"
    assert artifacts[0]["artifact_type"] == "output"
    assert read_response.json()["payload"] == {"candidates": []}
    assert read_response.json()["artifact"]["sha256"] == artifacts[0]["sha256"]
    lifecycle = lifecycle_response.json()["tool_run_lifecycle"]
    assert lifecycle["previous_status"] == "prepared"
    assert lifecycle["status"] == "completed"
    assert lifecycle["manifest"]["status_note"] == "candidate summary reviewed"
    summary = summary_response.json()["tool_run_summary"]
    assert summary["status"] == "completed"
    assert summary["artifact_count"] == 1
    assert summary["artifact_counts_by_type"]["output"] == 1
    assert summary["artifacts"][0]["sha256"] == artifacts[0]["sha256"]
    ai_context = ai_context_response.json()["context_pack"]
    assert ai_context["summary"]["artifact_count"] == 1
    assert ai_context["artifact_payloads"][0]["payload"] == {"candidates": []}
    assert ai_context["external_ai_call_performed"] is False
    rmtree(workspace_path)
