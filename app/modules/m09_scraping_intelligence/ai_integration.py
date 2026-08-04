"""Local LaIA/Mistral integration for M09 scraping intelligence.

This module is the Ronda 13 bridge between M09 and ``app.ai``.  It prepares
bounded prompts, calls the configured local Ollama/Mistral client only when AI is
enabled, and validates JSON responses before turning them into evidence.  It does
not execute scraping, bypass CAPTCHAs, rotate proxies, or call external AI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Protocol
from uuid import NAMESPACE_URL, uuid5

from app.ai.local_llm_client import LLMRequest, LLMResponse, LocalLLMClient
from app.config import Settings, get_settings
from app.contracts.evidence_contract import EVIDENCE_QUALITY_MEDIUM, EvidenceRecord, RESULT_SUCCESS
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_LOCAL_AI, TechniqueExecutionContext, TechniqueExecutionResult
from app.core.errors import ConfigurationError, ContractError
from app.core.permission_levels import PERMISSION_PASSIVE
from app.modules.m09_scraping_intelligence.techniques import M09_MODULE_ID

M09_AI_PROMPT_MODE = "m09_scraping_local_mistral_json_only"
M09_AI_MAX_GOAL_CHARS = 2_000
M09_AI_MAX_CONTEXT_CHARS = 12_000
M09_ALLOWED_BASE_TECHNIQUES = {
    "scraping.advanced.rss_atom",
    "scraping.crawler.output_parser",
    "scraping.export.csv",
    "scraping.export.json",
    "scraping.parser.html_extraction",
    "scraping.parser.json_rows_normalizer",
    "scraping.storage.sqlite_table_writer",
}


def _string_parameter(parameters: dict[str, Any], name: str) -> str:
    value = parameters.get(name)
    text = "" if value is None else str(value).strip()
    if not text:
        raise ContractError(f"{name} cannot be empty.")
    return text


def _ai_evidence(context: TechniqueExecutionContext, technique_id: str, suffix: str, summary: str, content: dict[str, Any]) -> EvidenceRecord:
    evidence_id = f"ev-{uuid5(NAMESPACE_URL, f'{context.run_id}:{technique_id}:{suffix}')}"
    return EvidenceRecord(
        evidence_id=evidence_id,
        run_id=context.run_id,
        target_id=context.target_id,
        technique_id=technique_id,
        module_id=M09_MODULE_ID,
        evidence_type=suffix,
        quality=EVIDENCE_QUALITY_MEDIUM,
        summary=summary,
        content=content,
        source="m09-local-ai",
        demo=False,
        real_execution=True,
        created_at=datetime.now(UTC).isoformat(),
    )


class M09LLMClient(Protocol):
    """Protocol implemented by LocalLLMClient and tests."""

    def is_configured(self) -> bool:
        """Return whether the local AI backend can be called."""

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate one local response."""


@dataclass(frozen=True, slots=True)
class ScrapingPlanRequest:
    """Bounded natural-language M09 planning request."""

    natural_language_goal: str
    target: str
    available_techniques: tuple[str, ...] = tuple(sorted(M09_ALLOWED_BASE_TECHNIQUES))
    known_schema: dict[str, Any] = field(default_factory=dict)
    sample_rows: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True, slots=True)
class ScrapingTableAnalysisRequest:
    """Bounded table-analysis request for local Mistral."""

    question: str
    rows: tuple[dict[str, Any], ...]
    schema: dict[str, Any] = field(default_factory=dict)
    max_rows: int = 50


def _bounded_text(value: object, limit: int) -> str:
    text = "" if value is None else str(value)
    return text if len(text) <= limit else text[:limit] + "…"


def _json_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
    return _bounded_text(encoded, M09_AI_MAX_CONTEXT_CHARS)


def _extract_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if not candidate:
        raise ContractError("M09 AI response is empty.")
    if not (candidate.startswith("{") and candidate.endswith("}")):
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ContractError("M09 AI response does not contain a JSON object.")
        candidate = candidate[start : end + 1]
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise ContractError("M09 AI response JSON could not be parsed.") from error
    if not isinstance(payload, dict):
        raise ContractError("M09 AI response JSON must be an object.")
    return payload


def build_scraping_plan_prompt(request: ScrapingPlanRequest) -> str:
    """Render a ChatML prompt for local Mistral to plan only registered M09 base techniques."""
    goal = _bounded_text(request.natural_language_goal.strip(), M09_AI_MAX_GOAL_CHARS)
    if not goal:
        raise ContractError("natural_language_goal cannot be empty.")
    if not request.target.strip():
        raise ContractError("target cannot be empty.")
    allowed = [technique for technique in request.available_techniques if technique in M09_ALLOWED_BASE_TECHNIQUES]
    if not allowed:
        raise ContractError("available_techniques must include at least one allowed M09 base technique.")
    payload = {
        "mode": M09_AI_PROMPT_MODE,
        "task": "create_non_executing_scraping_plan",
        "natural_language_goal": goal,
        "target": request.target.strip(),
        "available_techniques": allowed,
        "known_schema": request.known_schema,
        "sample_rows": list(request.sample_rows[:5]),
        "required_output_schema": {
            "objective": "string",
            "target": "string",
            "recommended_techniques": [{"technique_id": "one allowed id", "reason": "string", "required_parameters": {}}],
            "missing_inputs": ["string"],
            "rate_limit_profile": "string",
            "storage_profile": "string",
            "safety_notes": ["string"],
            "execution_implied": False,
        },
    }
    return (
        "<|system|>\n"
        "Eres LaIA/Mistral local para M09. Devuelve solo JSON compacto. "
        "No ejecutes scraping, no inventes técnicas, no propongas bypass, CAPTCHA, proxy rotation ni X4/X5 privado.\n"
        "<|user|>\n"
        f"{_json_payload(payload)}\n"
        "<|assistant|>\n"
    )


def validate_scraping_plan_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a M09 plan JSON payload."""
    if payload.get("execution_implied") is not False:
        raise ContractError("M09 AI plan must set execution_implied=false.")
    recommended = payload.get("recommended_techniques")
    if not isinstance(recommended, list) or not recommended:
        raise ContractError("M09 AI plan must include recommended_techniques.")
    normalized_recommendations: list[dict[str, Any]] = []
    for item in recommended:
        if not isinstance(item, dict):
            raise ContractError("M09 AI recommended_techniques entries must be objects.")
        technique_id = str(item.get("technique_id", "")).strip()
        if technique_id not in M09_ALLOWED_BASE_TECHNIQUES:
            raise ContractError("M09 AI plan referenced an unavailable or disallowed technique.")
        params = item.get("required_parameters", {})
        if not isinstance(params, dict):
            raise ContractError("M09 AI required_parameters must be an object.")
        normalized_recommendations.append({"technique_id": technique_id, "reason": str(item.get("reason", "")).strip(), "required_parameters": params})
    normalized = {
        "objective": str(payload.get("objective", "")).strip(),
        "target": str(payload.get("target", "")).strip(),
        "recommended_techniques": normalized_recommendations,
        "missing_inputs": [str(item) for item in payload.get("missing_inputs", []) if str(item).strip()],
        "rate_limit_profile": str(payload.get("rate_limit_profile", "operator_defined")).strip() or "operator_defined",
        "storage_profile": str(payload.get("storage_profile", "sqlite_or_export")).strip() or "sqlite_or_export",
        "safety_notes": [str(item) for item in payload.get("safety_notes", []) if str(item).strip()],
        "execution_implied": False,
    }
    if not normalized["objective"] or not normalized["target"]:
        raise ContractError("M09 AI plan must include objective and target.")
    return normalized


def build_table_analysis_prompt(request: ScrapingTableAnalysisRequest) -> str:
    """Render a ChatML prompt for local Mistral table analysis over supplied rows only."""
    question = _bounded_text(request.question.strip(), M09_AI_MAX_GOAL_CHARS)
    if not question:
        raise ContractError("question cannot be empty.")
    rows = list(request.rows[: max(1, request.max_rows)])
    payload = {
        "mode": M09_AI_PROMPT_MODE,
        "task": "analyze_supplied_rows_only",
        "question": question,
        "schema": request.schema,
        "rows": rows,
        "row_count_supplied": len(request.rows),
        "required_output_schema": {
            "answer": "string",
            "observations": ["string"],
            "suggested_exports": ["csv|json|sqlite"],
            "missing_data": ["string"],
            "execution_implied": False,
        },
    }
    return (
        "<|system|>\n"
        "Eres LaIA/Mistral local para analizar datos M09 ya suministrados. Devuelve solo JSON compacto. "
        "No hagas llamadas web, no inventes filas y no ejecutes herramientas.\n"
        "<|user|>\n"
        f"{_json_payload(payload)}\n"
        "<|assistant|>\n"
    )


def validate_table_analysis_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a M09 table-analysis JSON payload."""
    if payload.get("execution_implied") is not False:
        raise ContractError("M09 table analysis must set execution_implied=false.")
    answer = str(payload.get("answer", "")).strip()
    if not answer:
        raise ContractError("M09 table analysis answer cannot be empty.")
    allowed_exports = {"csv", "json", "sqlite"}
    return {
        "answer": answer,
        "observations": [str(item) for item in payload.get("observations", []) if str(item).strip()],
        "suggested_exports": [str(item) for item in payload.get("suggested_exports", []) if str(item) in allowed_exports],
        "missing_data": [str(item) for item in payload.get("missing_data", []) if str(item).strip()],
        "execution_implied": False,
    }


class M09ScrapingAIService:
    """Local Mistral-backed M09 assistant with JSON validation."""

    def __init__(self, settings: Settings | None = None, client: M09LLMClient | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = client or LocalLLMClient(
            base_url=self.settings.ollama_base_url,
            timeout_seconds=self.settings.ai_request_timeout_seconds,
            enabled=self.settings.ai_enabled and self.settings.mistral_enabled,
        )

    def _model(self) -> str:
        return self.settings.mistral_model

    def _generate_json(self, prompt: str) -> dict[str, Any]:
        if not self.client.is_configured():
            raise ConfigurationError("M09 local Mistral integration is disabled or not configured.")
        response = self.client.generate(LLMRequest(prompt=prompt, model=self._model(), temperature=0.0, timeout_seconds=self.settings.ai_request_timeout_seconds))
        return _extract_json_object(response.text)

    def plan(self, request: ScrapingPlanRequest) -> dict[str, Any]:
        """Generate and validate a non-executing scraping plan."""
        return validate_scraping_plan_response(self._generate_json(build_scraping_plan_prompt(request)))

    def analyze_table(self, request: ScrapingTableAnalysisRequest) -> dict[str, Any]:
        """Generate and validate an analysis over supplied rows only."""
        return validate_table_analysis_response(self._generate_json(build_table_analysis_prompt(request)))


class AiNaturalLanguagePlanTechnique(BaseTechnique):
    """Use local LaIA/Mistral to plan M09 base techniques without executing them."""

    technique_id = "scraping.ai.natural_language_plan"
    module_id = M09_MODULE_ID
    display_name = "M09 local AI natural-language plan"
    description = "Ask the configured local Mistral model for a JSON plan using only registered M09 base techniques."
    tool_name = "Dolphin Mistral Nemo 12B"
    recommended_version = "local_ollama_configured_model"
    runtime = "local_ai"
    worker = "AIWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["natural_language_goal", "target"]
    optional_inputs = ["known_schema", "sample_rows"]
    expected_evidence = ["plan_json", "normalized_json"]
    input_schema = {"natural_language_goal": {"type": "string"}, "target": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "natural_language_goal", "label": "Scraping goal", "type": "textarea"}]
    success_markers = ["plan_json"]
    failure_markers = ["ai_unavailable", "invalid_ai_json"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_LOCAL_AI
    requires_user_implementation = False
    evidence_schema = {"plan_json": "dict"}
    version_lock_id = "m09_scraping_intelligence/local-ai-plan"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        service = M09ScrapingAIService()
        sample_rows = context.parameters.get("sample_rows", [])
        if not isinstance(sample_rows, list):
            raise ContractError("sample_rows must be a list of objects.")
        request = ScrapingPlanRequest(
            natural_language_goal=_string_parameter(context.parameters, "natural_language_goal"),
            target=_string_parameter(context.parameters, "target"),
            known_schema=context.parameters.get("known_schema", {}) if isinstance(context.parameters.get("known_schema", {}), dict) else {},
            sample_rows=tuple(item for item in sample_rows if isinstance(item, dict)),
        )
        plan = service.plan(request)
        content = {"plan_json": plan, "external_ai_call_performed": False, "local_ai_call_performed": True}
        evidence = _ai_evidence(context, self.technique_id, "plan_json", "Local Mistral generated a validated M09 scraping plan.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class AiTableAnalysisTechnique(BaseTechnique):
    """Use local LaIA/Mistral to analyze supplied M09 rows only."""

    technique_id = "scraping.ai.table_analysis"
    module_id = M09_MODULE_ID
    display_name = "M09 local AI table analysis"
    description = "Ask the configured local Mistral model to analyze supplied rows without fetching new data."
    tool_name = "Dolphin Mistral Nemo 12B"
    recommended_version = "local_ollama_configured_model"
    runtime = "local_ai"
    worker = "AIWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = ["question", "rows"]
    optional_inputs = ["schema", "max_rows"]
    expected_evidence = ["analysis_json", "normalized_json"]
    input_schema = {"question": {"type": "string"}, "rows": {"type": "array"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "question", "label": "Analysis question", "type": "textarea"}]
    success_markers = ["analysis_json"]
    failure_markers = ["ai_unavailable", "invalid_ai_json"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_LOCAL_AI
    requires_user_implementation = False
    evidence_schema = {"analysis_json": "dict"}
    version_lock_id = "m09_scraping_intelligence/local-ai-table-analysis"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        service = M09ScrapingAIService()
        rows = context.parameters.get("rows")
        if not isinstance(rows, list) or not all(isinstance(item, dict) for item in rows):
            raise ContractError("rows must be a list of objects.")
        request = ScrapingTableAnalysisRequest(
            question=_string_parameter(context.parameters, "question"),
            rows=tuple(dict(item) for item in rows),
            schema=context.parameters.get("schema", {}) if isinstance(context.parameters.get("schema", {}), dict) else {},
            max_rows=int(context.parameters.get("max_rows", 50)),
        )
        analysis = service.analyze_table(request)
        content = {"analysis_json": analysis, "external_ai_call_performed": False, "local_ai_call_performed": True}
        evidence = _ai_evidence(context, self.technique_id, "analysis_json", "Local Mistral generated validated M09 table analysis.", content)
        return TechniqueExecutionResult(self.technique_id, M09_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


@dataclass(frozen=True, slots=True)
class ScrapingAiEvidencePipelineResult:
    """End-to-end M09 scraping-to-AI-to-EvidenceStore result."""

    analysis: dict[str, Any]
    stored_evidence_id: str
    stored_content_path: str
    row_count: int


def run_scraping_ai_evidence_pipeline(
    *,
    context: TechniqueExecutionContext,
    rows: list[dict[str, Any]],
    question: str,
    evidence_store: Any,
    ai_service: M09ScrapingAIService,
    schema: dict[str, Any] | None = None,
) -> ScrapingAiEvidencePipelineResult:
    """Analyze scraped rows with local AI and persist validated output to EvidenceStore.

    The function accepts already-scraped/normalized records, calls the configured
    local M09 AI service, validates the model JSON through ``analyze_table``, and
    stores a first-class EvidenceRecord. It never fetches URLs and never bypasses
    the EvidenceStore custody path.
    """
    if not rows or not all(isinstance(item, dict) for item in rows):
        raise ContractError("rows must be a non-empty list of scraped record objects.")
    analysis = ai_service.analyze_table(ScrapingTableAnalysisRequest(question=question, rows=tuple(dict(item) for item in rows), schema=schema or {}))
    content = {
        "pipeline": "scraping_to_ai_to_evidence_store",
        "scraped_rows": rows,
        "row_count": len(rows),
        "analysis_json": analysis,
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
        "evidence_store_write_requested": True,
    }
    record = _ai_evidence(context, "scraping.ai.pipeline_evidence_store", "pipeline_analysis_json", "M09 scraping-to-AI pipeline stored validated analysis in EvidenceStore.", content)
    stored = evidence_store.store_record(record)
    return ScrapingAiEvidencePipelineResult(analysis=analysis, stored_evidence_id=stored.evidence_id, stored_content_path=stored.content_path, row_count=len(rows))
