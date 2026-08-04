"""Module AI context pack contract tests."""

import json

from app.ai.module_context import (
    MODULE_CONTEXT_MODE,
    MODULE_CONTEXT_PURPOSE,
    build_module_context_pack,
    explain_module_for_ai,
)
from app.config import Settings


def test_module_context_pack_is_bounded_json_safe_and_complete() -> None:
    settings = Settings(_env_file=None, deepseek_api_key="private-secret", ai_enabled=True, mistral_enabled=True)

    pack = build_module_context_pack(settings=settings)
    payload = pack.to_dict()
    encoded = pack.to_json()

    assert payload["purpose"] == MODULE_CONTEXT_PURPOSE
    assert payload["mode"] == MODULE_CONTEXT_MODE
    assert payload["module_count"] == 20
    assert payload["modules"][0]["module"]["module_id"] == "m01_osint"
    assert payload["modules"][-1]["module"]["module_id"] == "m20_future_expansion"
    assert payload["ai_settings"]["deepseek_api_key"] == "set"
    assert "private-secret" not in encoded
    assert json.loads(encoded)["module_count"] == 20


def test_module_context_pack_can_hide_reserved_modules() -> None:
    pack = build_module_context_pack(include_reserved=False, settings=Settings(_env_file=None))
    payload = pack.to_dict()

    assert payload["module_count"] == 16
    assert all(item["module"]["official"] is True for item in payload["modules"])


def test_reserved_module_explanation_requires_user_definition_without_execution_claim() -> None:
    explanation = explain_module_for_ai("m17_hackrf_sdr", settings=Settings(_env_file=None))

    assert explanation["module_id"] == "m17_hackrf_sdr"
    assert explanation["requires_user_definition"] is True
    assert explanation["next_user_required"] is True
    assert explanation["execution_implied"] is False
    assert "does not execute tools" in explanation["explanation"]
    assert explanation["context"]["readiness_inputs"]["external_ai_call_performed"] is False


def test_official_module_explanation_keeps_workspace_and_model_context() -> None:
    settings = Settings(_env_file=None, ai_backend="ollama")

    explanation = explain_module_for_ai("m16_ops_quality", settings=settings)

    assert explanation["module_id"] == "m16_ops_quality"
    assert explanation["workspace_path"] == "storage/workspaces/m16_ops_quality"
    assert explanation["ai_backend"] == "ollama"
    assert explanation["mistral_model"] == "CognitiveComputations/dolphin-mistral-nemo:12b"
    assert explanation["next_user_required"] is False


def test_module_context_reports_real_registered_technique_metadata_when_registry_is_supplied() -> None:
    from app.contracts.technique_contract import BaseTechnique, STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    from app.core.permission_levels import PERMISSION_PASSIVE
    from app.core.technique_registry import create_empty_registry

    class M16DummyTechnique(BaseTechnique):
        technique_id = "m16.dummy.readiness"
        module_id = "m16_ops_quality"
        display_name = "M16 Dummy Readiness"
        description = "Contract-only passive readiness metadata."
        tool_name = "python"
        recommended_version = "3.12"
        runtime = "python"
        worker = "ops"
        permission_level = PERMISSION_PASSIVE
        implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
        requires_user_implementation = True

    registry = create_empty_registry()
    registry.register(M16DummyTechnique)

    explanation = explain_module_for_ai("m16_ops_quality", settings=Settings(_env_file=None), registry=registry)
    module_context = explanation["context"]["module"]

    assert module_context["registered_technique_count"] == 1
    assert module_context["registered_techniques"][0]["technique_id"] == "m16.dummy.readiness"
    assert explanation["context"]["readiness_inputs"]["registered_technique_count"] == 1


def test_module_prompt_envelope_is_prompt_ready_but_performs_no_ai_call() -> None:
    from app.ai.module_context import build_module_prompt_envelope

    envelope = build_module_prompt_envelope("m17_hackrf_sdr", settings=Settings(_env_file=None)).to_dict()

    assert envelope["requested_module_id"] == "m17_hackrf_sdr"
    assert envelope["external_ai_call_performed"] is False
    assert envelope["response_schema"]["properties"]["execution_implied"]["const"] is False
    assert envelope["context_pack"]["module_count"] == 20
    assert any("reserved modules" in rule.lower() for rule in envelope["safety_rules"])


def test_module_context_pack_declares_required_laia_metadata_and_checksum() -> None:
    pack = build_module_context_pack(settings=Settings(_env_file=None))
    payload = pack.to_dict()

    assert payload["pack_type"] == "module_catalog_pack"
    assert payload["generated_at"].endswith("+00:00")
    assert payload["max_tokens"] == 6000
    assert payload["confidence"] == 1.0
    assert payload["status"] in {"READY", "PARTIAL"}
    assert len(payload["checksum"]) == 64
    assert "docs/LAIA_CONTEXT_PACKS.md" in payload["source_paths"]
    assert "app/core/module_catalog.py" in payload["source_paths"]


def test_module_context_checksum_is_based_on_payload_without_checksum_field() -> None:
    pack = build_module_context_pack(settings=Settings(_env_file=None))
    payload_without_checksum = pack.to_dict(include_checksum=False)

    assert "checksum" not in payload_without_checksum
    assert pack.checksum != ""
    assert pack.to_dict()["checksum"] == pack.checksum
