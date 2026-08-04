"""AI/Hermes configuration contract tests."""

import json

import pytest
from app.config import Settings
from app.core.errors import ConfigurationError


def test_settings_defaults_keep_ai_disabled_and_mistral_model_pinned() -> None:
    settings = Settings(_env_file=None)

    assert settings.ai_enabled is False
    assert settings.mistral_enabled is False
    assert settings.angel_enabled is False
    assert settings.ai_backend == "ollama"
    assert settings.mistral_model == "CognitiveComputations/dolphin-mistral-nemo:12b"
    assert settings.mistral_model_display_name == "Dolphin Mistral Nemo 12B"
    assert settings.mistral_prompt_template == "chatml"
    assert settings.mistral_context_window_tokens == 128_000
    assert settings.mistral_guardrails_required is True
    assert settings.deepseek_model == "deepseek-v4-pro"
    assert settings.deepseek_fast_model == "deepseek-v4-flash"
    assert settings.deepseek_pro_model == "deepseek-v4-pro"
    assert settings.angel_workspace == "modules/laboratory"


def test_sanitized_ai_settings_do_not_expose_deepseek_api_key() -> None:
    settings = Settings(_env_file=None, deepseek_api_key="private-secret", ai_enabled=False, mistral_enabled=True)
    sanitized = settings.sanitized_ai_settings()
    payload = json.dumps(sanitized, ensure_ascii=False)

    assert sanitized["deepseek_api_key"] == "set"
    assert sanitized["mistral_enabled"] is False
    assert sanitized["mistral_model_display_name"] == "Dolphin Mistral Nemo 12B"
    assert sanitized["mistral_prompt_template"] == "chatml"
    assert sanitized["mistral_context_window_tokens"] == 128_000
    assert sanitized["mistral_guardrails_required"] is True
    assert sanitized["angel_enabled"] is False
    assert "private-secret" not in payload


def test_mistral_model_is_strictly_pinned() -> None:
    with pytest.raises(ConfigurationError, match="MISTRAL_MODEL"):
        Settings(_env_file=None, mistral_model="mistral:latest")


def test_mistral_dolphin_profile_rejects_invalid_template_and_context() -> None:
    with pytest.raises(ConfigurationError, match="MISTRAL_PROMPT_TEMPLATE"):
        Settings(_env_file=None, mistral_prompt_template="alpaca")
    with pytest.raises(ConfigurationError, match="MISTRAL_CONTEXT_WINDOW_TOKENS"):
        Settings(_env_file=None, mistral_context_window_tokens=4096)


def test_deepseek_model_is_limited_to_known_policy_models() -> None:
    flash = Settings(_env_file=None, deepseek_model="deepseek-v4-flash")
    pro = Settings(_env_file=None, deepseek_model="deepseek-v4-pro")

    assert flash.deepseek_model == "deepseek-v4-flash"
    assert pro.deepseek_model == "deepseek-v4-pro"
    with pytest.raises(ConfigurationError, match="DEEPSEEK_MODEL"):
        Settings(_env_file=None, deepseek_model="unknown-model")


def test_repository_paths_must_be_relative_for_windows_portability() -> None:
    with pytest.raises(ConfigurationError, match="repository-relative"):
        Settings(_env_file=None, angel_workspace="/tmp/hermes")
    with pytest.raises(ConfigurationError, match="repository-relative"):
        Settings(_env_file=None, angel_prompt_path="C:/secret/prompt.md")


def test_env_example_documents_required_ai_and_hermes_variables() -> None:
    env_example = open(".env.example", encoding="utf-8").read()

    assert "AI_ENABLED=0" in env_example
    assert "MISTRAL_ENABLED=0" in env_example
    assert "MISTRAL_MODEL=CognitiveComputations/dolphin-mistral-nemo:12b" in env_example
    assert "MISTRAL_MODEL_DISPLAY_NAME=Dolphin Mistral Nemo 12B" in env_example
    assert "MISTRAL_PROMPT_TEMPLATE=chatml" in env_example
    assert "MISTRAL_CONTEXT_WINDOW_TOKENS=128000" in env_example
    assert "MISTRAL_GUARDRAILS_REQUIRED=1" in env_example
    assert "ANGEL_ENABLED=0" in env_example
    assert "DEEPSEEK_API_KEY=" in env_example
    assert "DEEPSEEK_MODEL=deepseek-v4-pro" in env_example
    assert "DEEPSEEK_FAST_MODEL=deepseek-v4-flash" in env_example
    assert "private-secret" not in env_example
