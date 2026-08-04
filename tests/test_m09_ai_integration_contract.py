import json

import pytest

from app.ai.local_llm_client import LLMRequest, LLMResponse
from sqlalchemy import create_engine

from app.config import Settings
from app.contracts.technique_contract import STATUS_READY_LOCAL_AI, TechniqueExecutionContext
from app.core.errors import ContractError
from app.core.evidence_store import EvidenceStore
from app.db.session import create_session_factory, init_db
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.registry_loader import load_registry_from_package
from app.modules.m09_scraping_intelligence.ai_integration import (
    M09_ALLOWED_BASE_TECHNIQUES,
    M09ScrapingAIService,
    ScrapingPlanRequest,
    ScrapingTableAnalysisRequest,
    build_scraping_plan_prompt,
    build_table_analysis_prompt,
    validate_scraping_plan_response,
    run_scraping_ai_evidence_pipeline,
    validate_table_analysis_response,
)


class FakeLLMClient:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.requests: list[LLMRequest] = []

    def is_configured(self) -> bool:
        return True

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text=json.dumps(self.response), model=request.model, raw={"fake": True})


def _settings() -> Settings:
    return Settings(ai_enabled=True, mistral_enabled=True)


def test_m09_ai_techniques_register_as_local_ai_non_executing() -> None:
    registry = load_registry_from_package("app.modules.m09_scraping_intelligence")
    ids = registry.list_ids()

    assert "scraping.ai.natural_language_plan" in ids
    assert "scraping.ai.table_analysis" in ids
    for technique_id in ("scraping.ai.natural_language_plan", "scraping.ai.table_analysis"):
        technique = registry.require(technique_id)()
        technique.validate_metadata()
        assert technique.permission_level == PERMISSION_PASSIVE
        assert technique.implementation_status == STATUS_READY_LOCAL_AI
        assert technique.requires_user_implementation is False
        assert technique.requires_network is False


def test_build_scraping_plan_prompt_limits_ai_to_registered_base_techniques() -> None:
    prompt = build_scraping_plan_prompt(
        ScrapingPlanRequest(
            natural_language_goal="Normalize the supplied HTML and export rows",
            target="example.com",
            available_techniques=tuple(sorted(M09_ALLOWED_BASE_TECHNIQUES | {"scraping.ai.table_analysis"})),
            sample_rows=({"name": "alpha"},),
        )
    )

    assert "create_non_executing_scraping_plan" in prompt
    assert "scraping.parser.html_extraction" in prompt
    assert "scraping.ai.table_analysis" not in prompt
    assert "execution_implied" in prompt


def test_scraping_plan_response_rejects_unavailable_or_executing_actions() -> None:
    with pytest.raises(ContractError):
        validate_scraping_plan_response({"execution_implied": True, "recommended_techniques": []})
    with pytest.raises(ContractError):
        validate_scraping_plan_response(
            {
                "objective": "bad",
                "target": "example.com",
                "recommended_techniques": [{"technique_id": "scraping.evasion.proxychains_profile", "reason": "bypass", "required_parameters": {}}],
                "execution_implied": False,
            }
        )


def test_m09_ai_service_calls_local_llm_and_validates_plan_json() -> None:
    fake = FakeLLMClient(
        {
            "objective": "Normalize supplied rows",
            "target": "example.com",
            "recommended_techniques": [
                {"technique_id": "scraping.parser.json_rows_normalizer", "reason": "Input is JSON", "required_parameters": {"record_path": "data.items"}}
            ],
            "missing_inputs": [],
            "rate_limit_profile": "not_applicable_supplied_data",
            "storage_profile": "sqlite",
            "safety_notes": ["Use supplied data only"],
            "execution_implied": False,
        }
    )
    service = M09ScrapingAIService(settings=_settings(), client=fake)

    plan = service.plan(ScrapingPlanRequest(natural_language_goal="Parse JSON", target="example.com"))

    assert plan["recommended_techniques"][0]["technique_id"] == "scraping.parser.json_rows_normalizer"
    assert plan["execution_implied"] is False
    assert fake.requests[0].model == "CognitiveComputations/dolphin-mistral-nemo:12b"


def test_table_analysis_prompt_and_service_use_supplied_rows_only() -> None:
    prompt = build_table_analysis_prompt(ScrapingTableAnalysisRequest(question="Summarize", rows=({"name": "alpha", "score": 2},)))
    assert "analyze_supplied_rows_only" in prompt
    assert "no ejecutes herramientas" in prompt

    fake = FakeLLMClient(
        {
            "answer": "alpha has the highest score",
            "observations": ["one row supplied"],
            "suggested_exports": ["json", "unsupported"],
            "missing_data": [],
            "execution_implied": False,
        }
    )
    analysis = M09ScrapingAIService(settings=_settings(), client=fake).analyze_table(
        ScrapingTableAnalysisRequest(question="Summarize", rows=({"name": "alpha", "score": 2},))
    )

    assert analysis == {
        "answer": "alpha has the highest score",
        "observations": ["one row supplied"],
        "suggested_exports": ["json"],
        "missing_data": [],
        "execution_implied": False,
    }


def test_table_analysis_response_requires_non_execution_flag() -> None:
    with pytest.raises(ContractError):
        validate_table_analysis_response({"answer": "ok", "execution_implied": True})


def test_m09_scraping_ai_evidence_pipeline_stores_validated_analysis(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'evidence.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    store = EvidenceStore(session_factory(), base_path=tmp_path / "evidence")
    fake = FakeLLMClient(
        {
            "answer": "Found two public records",
            "observations": ["two rows supplied"],
            "suggested_exports": ["json"],
            "missing_data": [],
            "execution_implied": False,
        }
    )
    context = TechniqueExecutionContext(target_id="target-m09", run_id="run-m09", mode="controlled", parameters={}, confirmed=True)

    result = run_scraping_ai_evidence_pipeline(
        context=context,
        rows=[{"title": "Alpha", "url": "https://example.com/a"}, {"title": "Beta", "url": "https://example.com/b"}],
        question="Summarize supplied scraped rows",
        evidence_store=store,
        ai_service=M09ScrapingAIService(settings=_settings(), client=fake),
    )
    stored_content = store.read_content(result.stored_evidence_id)

    assert result.row_count == 2
    assert result.analysis["answer"] == "Found two public records"
    assert stored_content is not None
    assert stored_content["content"]["pipeline"] == "scraping_to_ai_to_evidence_store"
    assert stored_content["content"]["analysis_json"]["execution_implied"] is False
    assert stored_content["real_execution"] is True
