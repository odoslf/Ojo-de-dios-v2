"""Hermes Agent assistance service backed by DeepSeek when explicitly enabled."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.ai.deepseek_client import DeepSeekChatRequest, DeepSeekChatResponse, DeepSeekClient, DeepSeekMessage
from app.config import Settings
from app.core.errors import ConfigurationError, ContractError

HERMES_ASSIST_MODE = "deepseek_json_assist_no_execution"
HERMES_MAX_CONTEXT_CHARS = 16_000
HERMES_MAX_QUESTION_CHARS = 2_000


class HermesChatClient(Protocol):
    """Protocol implemented by DeepSeekClient and test doubles."""

    def chat(self, request: DeepSeekChatRequest) -> DeepSeekChatResponse:
        """Send one chat request and return a normalized response."""


@dataclass(frozen=True, slots=True)
class HermesAssistRequest:
    """Bounded request for external Hermes assistance."""

    question: str
    context: dict[str, Any]
    purpose: str = "tooling_or_code_research"
    model: str = "deepseek-v4-pro"
    allow_pro_model: bool = False
    max_tokens: int = 1200
    reasoning_effort: str = "low"


@dataclass(frozen=True, slots=True)
class HermesAssistResponse:
    """Normalized Hermes assistance response."""

    model: str
    content: str
    mode: str = HERMES_ASSIST_MODE
    external_ai_call_performed: bool = True
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "model": self.model,
            "content": self.content,
            "external_ai_call_performed": self.external_ai_call_performed,
            "raw": self.raw,
        }


def _bounded_json_context(context: dict[str, Any]) -> str:
    encoded = json.dumps(context, ensure_ascii=False, sort_keys=True, indent=2)
    return encoded if len(encoded) <= HERMES_MAX_CONTEXT_CHARS else encoded[:HERMES_MAX_CONTEXT_CHARS] + "…"


def _validate_request(request: HermesAssistRequest, settings: Settings) -> None:
    if not request.question.strip():
        raise ContractError("Hermes assistance question cannot be empty.")
    if len(request.question) > HERMES_MAX_QUESTION_CHARS:
        raise ContractError("Hermes assistance question is too large.")
    allowed_models = {settings.deepseek_model, settings.deepseek_fast_model, settings.deepseek_pro_model}
    if request.model not in allowed_models:
        raise ContractError("Hermes assistance model must match configured DeepSeek policy models.")
    if request.model == settings.deepseek_pro_model and settings.deepseek_model != settings.deepseek_pro_model:
        if not (request.allow_pro_model or settings.deepseek_allow_pro_without_explicit_approval):
            raise ContractError("DeepSeek pro model requires explicit approval.")
    if request.reasoning_effort not in {"low", "medium", "high"}:
        raise ContractError("Hermes reasoning_effort must be low, medium or high.")
    if request.max_tokens <= 0:
        raise ContractError("Hermes max_tokens must be positive.")


def build_hermes_deepseek_chat_request(request: HermesAssistRequest, settings: Settings) -> DeepSeekChatRequest:
    """Build a JSON-only DeepSeek request for Hermes assistance without sending it."""
    _validate_request(request, settings)
    system = (
        "You are Hermes Agent Lab for Ojo de Dios. Return only compact JSON. "
        "Do not execute tools, do not claim production readiness, do not expose secrets, "
        "and mark missing implementation as IMPLEMENTACION_USUARIO_REQUERIDA."
    )
    user_payload = {
        "purpose": request.purpose,
        "question": request.question,
        "context_json": _bounded_json_context(request.context),
        "required_output": {
            "answer": "short actionable answer",
            "risks": [],
            "missing_inputs": [],
            "execution_implied": False,
        },
    }
    return DeepSeekChatRequest(
        model=request.model,
        messages=(
            DeepSeekMessage(role="system", content=system),
            DeepSeekMessage(role="user", content=json.dumps(user_payload, ensure_ascii=False, sort_keys=True)),
        ),
        json_mode=True,
        thinking_enabled=False,
        reasoning_effort=request.reasoning_effort,
        max_tokens=request.max_tokens,
        temperature=0.0,
    )


class HermesDeepSeekAssistService:
    """Controlled DeepSeek-backed assistant for Hermes Agent Lab."""

    def __init__(self, settings: Settings, client: HermesChatClient | None = None) -> None:
        self.settings = settings
        self.client = client or DeepSeekClient(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_api_url,
            enabled=settings.ai_enabled and settings.angel_enabled,
        )

    def is_enabled(self) -> bool:
        """Return whether settings allow external Hermes assistance."""
        return self.settings.ai_enabled and self.settings.angel_enabled and bool(self.settings.deepseek_api_key)

    def ask_json(self, request: HermesAssistRequest) -> HermesAssistResponse:
        """Ask DeepSeek for JSON-only Hermes assistance after policy checks."""
        if not self.is_enabled():
            raise ConfigurationError("Hermes DeepSeek assistance is disabled or missing DEEPSEEK_API_KEY.")
        chat_request = build_hermes_deepseek_chat_request(request, self.settings)
        response = self.client.chat(chat_request)
        return HermesAssistResponse(model=response.model, content=response.content, raw=response.raw)
