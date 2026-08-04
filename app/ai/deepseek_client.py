"""DeepSeek API client for Hermes Agent external research assistance.

The client targets DeepSeek's OpenAI-compatible `/chat/completions` and
`/models` endpoints. It does not execute tools or touch production state; callers
must decide when external assistance is allowed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import requests

from app.core.errors import ConfigurationError, ContractError

DEEPSEEK_SUPPORTED_MODELS = {"deepseek-v4-flash", "deepseek-v4-pro"}
DEEPSEEK_DEFAULT_TIMEOUT_SECONDS = 60
DeepSeekMessageRole = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class DeepSeekMessage:
    """One DeepSeek chat message."""

    role: DeepSeekMessageRole
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True, slots=True)
class DeepSeekChatRequest:
    """DeepSeek chat completion request payload."""

    messages: tuple[DeepSeekMessage, ...]
    model: str = "deepseek-v4-pro"
    json_mode: bool = True
    thinking_enabled: bool = False
    reasoning_effort: str | None = None
    max_tokens: int | None = None
    temperature: float = 0.0

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [message.to_dict() for message in self.messages],
            "stream": False,
            "temperature": self.temperature,
        }
        if self.json_mode:
            payload["response_format"] = {"type": "json_object"}
        payload["thinking"] = {"type": "enabled" if self.thinking_enabled else "disabled"}
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        return payload


@dataclass(frozen=True, slots=True)
class DeepSeekChatResponse:
    """DeepSeek chat completion response normalized for callers."""

    model: str
    content: str
    raw: dict[str, Any] = field(default_factory=dict)


class DeepSeekClient:
    """Small DeepSeek HTTP client with explicit enablement and no secret logging."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        timeout_seconds: int = DEEPSEEK_DEFAULT_TIMEOUT_SECONDS,
        enabled: bool = False,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled

    def is_configured(self) -> bool:
        """Return whether DeepSeek calls are enabled and an API key is available."""
        return self.enabled is True and bool(self.api_key) and bool(self.base_url)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _ensure_configured(self) -> None:
        if not self.is_configured():
            raise ConfigurationError("DeepSeek client is not configured or Hermes Agent is disabled.")

    def list_models(self) -> tuple[str, ...]:
        """Return model ids from DeepSeek `/models`."""
        self._ensure_configured()
        response = requests.get(
            f"{self.base_url}/models",
            headers=self._headers(),
            timeout=self.timeout_seconds,
        )
        if not response.ok:
            raise ConfigurationError("DeepSeek models endpoint returned an error status.")
        payload = response.json()
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ContractError("DeepSeek models response must contain a data list.")
        return tuple(str(item.get("id")) for item in data if isinstance(item, dict) and item.get("id"))

    def chat(self, request: DeepSeekChatRequest) -> DeepSeekChatResponse:
        """Create one non-streaming DeepSeek chat completion."""
        self._ensure_configured()
        validate_deepseek_chat_request(request)
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=request.to_payload(),
            timeout=self.timeout_seconds,
        )
        if not response.ok:
            raise ConfigurationError("DeepSeek chat endpoint returned an error status.")
        payload = response.json()
        choices = payload.get("choices", [])
        if not choices or not isinstance(choices, list):
            raise ContractError("DeepSeek chat response must contain at least one choice.")
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ContractError("DeepSeek chat choice must be a JSON object.")
        message = first_choice.get("message", {})
        if not isinstance(message, dict):
            raise ContractError("DeepSeek chat choice message must be a JSON object.")
        return DeepSeekChatResponse(
            model=str(payload.get("model", request.model)),
            content=str(message.get("content", "")),
            raw=payload,
        )


def validate_deepseek_chat_request(request: DeepSeekChatRequest) -> None:
    """Validate a DeepSeek request before any network call."""
    if request.model not in DEEPSEEK_SUPPORTED_MODELS:
        raise ContractError("Unsupported DeepSeek model.")
    if not request.messages:
        raise ContractError("DeepSeek request requires at least one message.")
    for message in request.messages:
        if message.role not in {"system", "user", "assistant", "tool"}:
            raise ContractError("Unsupported DeepSeek message role.")
        if not message.content.strip():
            raise ContractError("DeepSeek message content cannot be empty.")
    if request.reasoning_effort and request.reasoning_effort not in {"low", "medium", "high"}:
        raise ContractError("DeepSeek reasoning_effort must be low, medium or high.")
    if request.max_tokens is not None and request.max_tokens <= 0:
        raise ContractError("DeepSeek max_tokens must be positive.")
