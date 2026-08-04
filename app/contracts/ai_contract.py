"""AI planning contracts for Ojo de Dios."""

from dataclasses import dataclass, field
from typing import Any

from app.core.errors import ContractError


@dataclass
class AIPlanStep:
    """Single step in an AI-generated plan contract."""

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
class AIPlan:
    """AI plan contract without any functional AI client."""

    intent: str
    target_type: str
    target_value: str
    recommended_plan: list[AIPlanStep] = field(default_factory=list)
    risk_score: float = 0.0
    confidence: float = 0.0
    user_explanation: str = ""


def validate_ai_plan(plan: AIPlan) -> None:
    """Validate an AI plan contract."""
    if not plan.intent:
        raise ContractError("Intent cannot be empty.")
    if not plan.target_type:
        raise ContractError("Target type cannot be empty.")
    if not plan.target_value:
        raise ContractError("Target value cannot be empty.")
    if not 0.0 <= plan.confidence <= 1.0:
        raise ContractError("Confidence must be between 0.0 and 1.0.")
    if not 0.0 <= plan.risk_score <= 1.0:
        raise ContractError("Risk score must be between 0.0 and 1.0.")
    for step in plan.recommended_plan:
        if step.step < 1:
            raise ContractError("Plan step number must be at least 1.")
        if not step.technique_id:
            raise ContractError("Step technique id cannot be empty.")
        if not step.module_id:
            raise ContractError("Step module id cannot be empty.")
        if not 0.0 <= step.priority <= 1.0:
            raise ContractError("Step priority must be between 0.0 and 1.0.")
