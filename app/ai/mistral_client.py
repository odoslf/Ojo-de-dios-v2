"""Mistral client backed by a local Ollama-compatible server."""

from app.ai.local_llm_client import LLMRequest, LocalLLMClient
from app.ai.schemas import AIPlanResponse
from app.ai.structured_output import parse_ai_plan_response
from app.core.errors import ConfigurationError


class MistralClient:
    """Convenience client for local Mistral generation through Ollama."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "CognitiveComputations/dolphin-mistral-nemo:12b",
        timeout_seconds: int = 30,
        enabled: bool = False,
    ) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.client = LocalLLMClient(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            enabled=enabled,
        )

    def is_configured(self) -> bool:
        """Return whether the underlying local client is configured."""
        return self.client.is_configured()

    def probe(self) -> dict[str, object]:
        """Return actual local backend/model availability without running inference."""
        return self.client.probe_model(self.model)

    def generate_text(self, prompt: str) -> str:
        """Generate raw text from a prompt."""
        if not self.is_configured():
            raise ConfigurationError("Mistral client is not configured or AI is disabled.")
        response = self.client.generate(
            LLMRequest(
                prompt=prompt,
                model=self.model,
                timeout_seconds=self.timeout_seconds,
            )
        )
        return response.text

    def generate_plan_response(self, prompt: str) -> AIPlanResponse:
        """Generate and parse a structured plan response."""
        return parse_ai_plan_response(self.generate_text(prompt))
