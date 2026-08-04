"""Dataclass schemas for local AI structured responses."""

from dataclasses import dataclass, field
from typing import Any

from app.core.errors import ContractError


@dataclass
class AITarget:
    """Target summary included in an AI response."""

    target_type: str
    value: str


@dataclass
class AIPlanStep:
    """Single recommended plan step returned by an AI response."""

    step: int
    technique_id: str
    module_id: str
    priority: float
    reason: str
    required_parameters: dict[str, Any] = field(default_factory=dict)
    missing_parameters: list[str] = field(default_factory=list)
    requires_user_logic: bool = True
    requires_confirmation: bool = True
    expected_evidence: list[str] = field(default_factory=list)


@dataclass
class AIFallbackStep:
    """Fallback routing hint returned by an AI response."""

    if_status: str
    next_technique_id: str
    reason: str


@dataclass
class AIPlanResponse:
    """Structured AI plan response contract."""

    intent: str
    target: AITarget
    recommended_plan: list[AIPlanStep] = field(default_factory=list)
    fallback_plan: list[AIFallbackStep] = field(default_factory=list)
    risk_score: float = 0.0
    confidence: float = 0.0
    user_explanation: str = ""


def _ensure_probability(value: float, field_name: str) -> None:
    if value < 0.0 or value > 1.0:
        raise ContractError(f"{field_name} must be between 0.0 and 1.0.")


def validate_ai_target(target: AITarget) -> None:
    """Validate the target section of an AI response."""
    if not target.target_type:
        raise ContractError("AI target type cannot be empty.")
    if not target.value:
        raise ContractError("AI target value cannot be empty.")


def validate_ai_plan_step(step: AIPlanStep) -> None:
    """Validate one recommended plan step."""
    if step.step < 1:
        raise ContractError("AI plan step number must be greater than or equal to 1.")
    if not step.technique_id:
        raise ContractError("AI plan step technique id cannot be empty.")
    if not step.module_id:
        raise ContractError("AI plan step module id cannot be empty.")
    _ensure_probability(step.priority, "AI plan step priority")
    if not step.reason:
        raise ContractError("AI plan step reason cannot be empty.")
    if not isinstance(step.required_parameters, dict):
        raise ContractError("AI plan step required_parameters must be a dict.")
    if not isinstance(step.missing_parameters, list):
        raise ContractError("AI plan step missing_parameters must be a list.")
    if not isinstance(step.expected_evidence, list):
        raise ContractError("AI plan step expected_evidence must be a list.")


def validate_ai_plan_response(response: AIPlanResponse) -> None:
    """Validate a complete AI plan response."""
    if not response.intent:
        raise ContractError("AI response intent cannot be empty.")
    validate_ai_target(response.target)
    _ensure_probability(response.risk_score, "AI response risk_score")
    _ensure_probability(response.confidence, "AI response confidence")
    for step in response.recommended_plan:
        validate_ai_plan_step(step)
    for fallback in response.fallback_plan:
        if not fallback.if_status:
            raise ContractError("AI fallback if_status cannot be empty.")
        if not fallback.next_technique_id:
            raise ContractError("AI fallback next_technique_id cannot be empty.")
        if not fallback.reason:
            raise ContractError("AI fallback reason cannot be empty.")
