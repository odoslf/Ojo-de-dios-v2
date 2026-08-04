"""Structured AI output parsing contract tests."""

import json

import pytest

from app.ai.structured_output import extract_json_object, parse_ai_plan_response, safe_parse_ai_plan_response
from app.core.errors import ContractError


def _payload() -> dict:
    return {
        "intent": "review_target",
        "target": {"target_type": "domain", "value": "example.local"},
        "recommended_plan": [
            {
                "step": 1,
                "technique_id": "provided.technique",
                "module_id": "provided_module",
                "priority": 0.5,
                "reason": "Included in provided context.",
            }
        ],
        "fallback_plan": [],
        "risk_score": 0.2,
        "confidence": 0.7,
        "user_explanation": "Structured response.",
    }


def test_extract_json_object_parses_pure_json() -> None:
    payload = {"hello": "world"}

    assert extract_json_object(json.dumps(payload)) == payload


def test_extract_json_object_parses_json_with_surrounding_text() -> None:
    payload = {"hello": "world"}

    assert extract_json_object(f"before {json.dumps(payload)} after") == payload


def test_extract_json_object_raises_when_no_json_object_exists() -> None:
    with pytest.raises(ContractError):
        extract_json_object("no structured object")


def test_parse_ai_plan_response_parses_valid_response() -> None:
    response = parse_ai_plan_response(json.dumps(_payload()))

    assert response.intent == "review_target"
    assert response.target.value == "example.local"
    assert len(response.recommended_plan) == 1


def test_safe_parse_ai_plan_response_returns_error_for_invalid_json() -> None:
    response, error = safe_parse_ai_plan_response("{invalid")

    assert response is None
    assert error is not None


def test_missing_recommended_plan_defaults_to_empty_list() -> None:
    payload = _payload()
    payload.pop("recommended_plan")

    response = parse_ai_plan_response(json.dumps(payload))

    assert response.recommended_plan == []
