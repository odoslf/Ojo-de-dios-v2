"""Local LLM client contract tests."""

import pytest

from app.ai.local_llm_client import LLMRequest, LocalLLMClient
from app.ai.mistral_client import MistralClient
from app.core.errors import ConfigurationError, ContractError


def test_disabled_local_llm_client_is_not_configured() -> None:
    assert LocalLLMClient(base_url="http://127.0.0.1:11434", enabled=False).is_configured() is False


def test_generate_disabled_local_llm_client_raises_configuration_error() -> None:
    client = LocalLLMClient(base_url="http://127.0.0.1:11434", enabled=False)

    with pytest.raises(ConfigurationError):
        client.generate(LLMRequest(prompt="hello", model="CognitiveComputations/dolphin-mistral-nemo:12b"))


def test_generate_enabled_local_llm_client_with_empty_prompt_raises_contract_error() -> None:
    client = LocalLLMClient(base_url="http://127.0.0.1:11434", enabled=True)

    with pytest.raises(ContractError):
        client.generate(LLMRequest(prompt="", model="CognitiveComputations/dolphin-mistral-nemo:12b"))


def test_disabled_mistral_client_is_not_configured() -> None:
    assert MistralClient(enabled=False).is_configured() is False


def test_disabled_mistral_client_generate_text_raises_configuration_error() -> None:
    client = MistralClient(enabled=False)

    with pytest.raises(ConfigurationError):
        client.generate_text("hello")
