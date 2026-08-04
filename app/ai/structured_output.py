"""Structured JSON output parsing for local AI responses."""

import json
from typing import Any

from app.ai.schemas import (
    AIFallbackStep,
    AIPlanResponse,
    AIPlanStep,
    AITarget,
    validate_ai_plan_response,
)
from app.core.errors import ContractError


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from a raw text response."""
    candidate = text.strip()
    if not candidate:
        raise ContractError("AI response is empty.")
    if not (candidate.startswith("{") and candidate.endswith("}")):
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ContractError("AI response does not contain a JSON object.")
        candidate = candidate[start : end + 1]
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise ContractError("AI response JSON could not be parsed.") from error
    if not isinstance(payload, dict):
        raise ContractError("AI response JSON must be an object.")
    return payload


def ai_plan_response_from_dict(payload: dict[str, Any]) -> AIPlanResponse:
    """Build and validate an AIPlanResponse from a dictionary."""
    target_payload = payload.get("target")
    if not isinstance(target_payload, dict):
        raise ContractError("AI response target must be an object.")

    recommended_payload = payload.get("recommended_plan", [])
    fallback_payload = payload.get("fallback_plan", [])
    if not isinstance(recommended_payload, list):
        raise ContractError("AI response recommended_plan must be a list.")
    if not isinstance(fallback_payload, list):
        raise ContractError("AI response fallback_plan must be a list.")

    response = AIPlanResponse(
        intent=payload.get("intent", ""),
        target=AITarget(
            target_type=target_payload.get("target_type", ""),
            value=target_payload.get("value", ""),
        ),
        recommended_plan=[AIPlanStep(**item) for item in recommended_payload],
        fallback_plan=[AIFallbackStep(**item) for item in fallback_payload],
        risk_score=payload.get("risk_score", 0.0),
        confidence=payload.get("confidence", 0.0),
        user_explanation=payload.get("user_explanation", ""),
    )
    validate_ai_plan_response(response)
    return response


def parse_ai_plan_response(text: str) -> AIPlanResponse:
    """Parse a raw AI response into the structured plan contract."""
    return ai_plan_response_from_dict(extract_json_object(text))


def safe_parse_ai_plan_response(text: str) -> tuple[AIPlanResponse | None, str | None]:
    """Parse a raw AI response without raising contract errors."""
    try:
        return parse_ai_plan_response(text), None
    except Exception as error:
        return None, str(error)
