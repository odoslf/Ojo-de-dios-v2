"""AI schema contract tests."""

import pytest

from app.ai.schemas import (
    AIFallbackStep,
    AIPlanResponse,
    AIPlanStep,
    AITarget,
    validate_ai_plan_response,
    validate_ai_plan_step,
    validate_ai_target,
)
from app.core.errors import ContractError


def _valid_response(**overrides) -> AIPlanResponse:
    data = {
        "intent": "review_target",
        "target": AITarget(target_type="domain", value="example.local"),
        "recommended_plan": [
            AIPlanStep(
                step=1,
                technique_id="provided.technique",
                module_id="provided_module",
                priority=0.5,
                reason="Included in provided context.",
            )
        ],
        "fallback_plan": [
            AIFallbackStep(
                if_status="MISSING_TOOL",
                next_technique_id="provided.fallback",
                reason="Use provided fallback when status matches.",
            )
        ],
        "risk_score": 0.2,
        "confidence": 0.7,
        "user_explanation": "Structured response.",
    }
    data.update(overrides)
    return AIPlanResponse(**data)


def test_valid_ai_plan_response_passes_validation() -> None:
    validate_ai_plan_response(_valid_response())


def test_confidence_greater_than_one_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_ai_plan_response(_valid_response(confidence=1.1))


def test_negative_risk_score_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_ai_plan_response(_valid_response(risk_score=-0.1))


def test_plan_step_zero_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_ai_plan_step(
            AIPlanStep(
                step=0,
                technique_id="provided.technique",
                module_id="provided_module",
                priority=0.5,
                reason="Invalid step number.",
            )
        )


def test_target_without_value_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_ai_target(AITarget(target_type="domain", value=""))


def test_incomplete_fallback_raises_contract_error() -> None:
    with pytest.raises(ContractError):
        validate_ai_plan_response(
            _valid_response(
                fallback_plan=[
                    AIFallbackStep(
                        if_status="FAILED",
                        next_technique_id="",
                        reason="Missing next step.",
                    )
                ]
            )
        )
