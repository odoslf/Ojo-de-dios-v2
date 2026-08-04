"""Generic local LLM client for Ollama-compatible backends."""

from dataclasses import dataclass, field
from typing import Any

import requests

from app.core.errors import ConfigurationError, ContractError


@dataclass
class LLMRequest:
    """Local LLM generation request."""

    prompt: str
    model: str
    temperature: float = 0.0
    timeout_seconds: int = 30


@dataclass
class LLMResponse:
    """Local LLM generation response."""

    text: str
    model: str
    raw: dict[str, Any] = field(default_factory=dict)


class LocalLLMClient:
    """Small Ollama-compatible local LLM client."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: int = 30,
        enabled: bool = False,
    ) -> None:
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled

    def is_configured(self) -> bool:
        """Return whether local AI calls are enabled and configured."""
        return self.enabled is True and bool(self.base_url)

    def probe_model(self, model: str) -> dict[str, Any]:
        """Read the local Ollama model catalog and report whether the requested model is available."""
        if not self.is_configured():
            raise ConfigurationError("Local LLM client is not configured or AI is disabled.")
        requested_model = str(model or "").strip()
        if not requested_model:
            raise ContractError("LLM model cannot be empty.")
        endpoint = f"{self.base_url.rstrip('/')}/api/tags"
        try:
            response = requests.get(endpoint, timeout=self.timeout_seconds)
        except requests.RequestException as exc:
            raise ConfigurationError(f"Local LLM backend is unavailable: {exc}") from exc
        if not response.ok:
            raise ConfigurationError(f"Local LLM backend returned HTTP {response.status_code} while listing models.")
        try:
            payload = response.json()
        except ValueError as exc:
            raise ConfigurationError("Local LLM backend returned invalid model catalog JSON.") from exc
        raw_models = payload.get("models", []) if isinstance(payload, dict) else []
        if not isinstance(raw_models, list):
            raise ConfigurationError("Local LLM backend returned an invalid model catalog.")
        available_models = sorted({
            name
            for item in raw_models
            if isinstance(item, dict)
            for name in (str(item.get("name", "")).strip(), str(item.get("model", "")).strip())
            if name
        })
        requested_has_tag = ":" in requested_model
        requested_model_key = requested_model.casefold()
        requested_base_key = requested_model.split(":", 1)[0].casefold()
        matched_models = [
            available_model
            for available_model in available_models
            if available_model.casefold() == requested_model_key
            or (
                not requested_has_tag
                and available_model.split(":", 1)[0].casefold() == requested_base_key
            )
        ]
        return {
            "backend_url": self.base_url.rstrip("/"),
            "requested_model": requested_model,
            "model_available": bool(matched_models),
            "matched_models": matched_models,
            "available_model_count": len(available_models),
            "available_models": available_models,
            "inference_performed": False,
        }

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using an Ollama-compatible local endpoint."""
        if not self.is_configured():
            raise ConfigurationError("Local LLM client is not configured or AI is disabled.")
        if not isinstance(request.prompt, str) or not request.prompt.strip():
            raise ContractError("LLM prompt cannot be empty.")
        if len(request.prompt) > 2_000_000:
            raise ContractError("LLM prompt exceeds the 2,000,000 character limit.")
        if not isinstance(request.model, str) or not request.model.strip():
            raise ContractError("LLM model cannot be empty.")
        if not isinstance(request.temperature, (int, float)) or not 0 <= float(request.temperature) <= 2:
            raise ContractError("LLM temperature must be between 0 and 2.")
        timeout = request.timeout_seconds or self.timeout_seconds
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ContractError("LLM timeout must be positive.")

        endpoint = f"{self.base_url.rstrip('/')}/api/generate"
        try:
            response = requests.post(
                endpoint,
                json={
                    "model": request.model.strip(),
                    "prompt": request.prompt,
                    "stream": False,
                    "options": {"temperature": float(request.temperature)},
                },
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise ConfigurationError(f"Local LLM backend is unavailable: {exc}") from exc
        if not response.ok:
            raise ConfigurationError(f"Local LLM backend returned HTTP {response.status_code} during generation.")
        try:
            payload = response.json()
        except ValueError as exc:
            raise ConfigurationError("Local LLM backend returned invalid generation JSON.") from exc
        if not isinstance(payload, dict):
            raise ConfigurationError("Local LLM backend returned an invalid generation response.")
        text = payload.get("response", "")
        if not isinstance(text, str):
            raise ConfigurationError("Local LLM backend generation response has no text field.")
        response_model = payload.get("model")
        model = response_model if isinstance(response_model, str) and response_model.strip() else request.model.strip()
        return LLMResponse(text=text, model=model, raw=payload)
