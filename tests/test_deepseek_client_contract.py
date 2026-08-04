"""DeepSeek client contract tests."""

import pytest

from app.ai.deepseek_client import (
    DeepSeekChatRequest,
    DeepSeekClient,
    DeepSeekMessage,
    validate_deepseek_chat_request,
)
from app.core.errors import ConfigurationError, ContractError


class _Response:
    def __init__(self, payload, ok=True):
        self._payload = payload
        self.ok = ok

    def json(self):
        return self._payload


def test_deepseek_request_payload_uses_v4_json_and_thinking_flags() -> None:
    request = DeepSeekChatRequest(
        model="deepseek-v4-pro",
        messages=(DeepSeekMessage(role="user", content="Return JSON."),),
        json_mode=True,
        thinking_enabled=True,
        reasoning_effort="high",
        max_tokens=128,
    )

    payload = request.to_payload()

    assert payload["model"] == "deepseek-v4-pro"
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["thinking"] == {"type": "enabled"}
    assert payload["reasoning_effort"] == "high"
    assert payload["stream"] is False


def test_deepseek_request_validation_rejects_legacy_or_empty_payloads() -> None:
    with pytest.raises(ContractError, match="Unsupported DeepSeek model"):
        validate_deepseek_chat_request(
            DeepSeekChatRequest(model="deepseek-chat", messages=(DeepSeekMessage(role="user", content="hello"),))
        )
    with pytest.raises(ContractError, match="at least one message"):
        validate_deepseek_chat_request(DeepSeekChatRequest(messages=()))
    with pytest.raises(ContractError, match="content cannot be empty"):
        validate_deepseek_chat_request(DeepSeekChatRequest(messages=(DeepSeekMessage(role="user", content="  "),)))


def test_deepseek_client_refuses_calls_when_disabled() -> None:
    client = DeepSeekClient(api_key="secret", enabled=False)

    with pytest.raises(ConfigurationError, match="not configured"):
        client.list_models()


def test_deepseek_client_lists_models_without_exposing_api_key(monkeypatch) -> None:
    captured = {}

    def fake_get(url, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return _Response({"object": "list", "data": [{"id": "deepseek-v4-flash"}, {"id": "deepseek-v4-pro"}]})

    monkeypatch.setattr("app.ai.deepseek_client.requests.get", fake_get)
    client = DeepSeekClient(api_key="secret", enabled=True, timeout_seconds=7)

    models = client.list_models()

    assert models == ("deepseek-v4-flash", "deepseek-v4-pro")
    assert captured["url"] == "https://api.deepseek.com/models"
    assert captured["headers"]["Authorization"] == "Bearer secret"
    assert captured["timeout"] == 7


def test_deepseek_client_chat_normalizes_first_choice(monkeypatch) -> None:
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["json"] = json
        return _Response(
            {
                "model": "deepseek-v4-pro",
                "choices": [{"message": {"role": "assistant", "content": "{\"ok\": true}"}}],
            }
        )

    monkeypatch.setattr("app.ai.deepseek_client.requests.post", fake_post)
    client = DeepSeekClient(api_key="secret", enabled=True)
    request = DeepSeekChatRequest(messages=(DeepSeekMessage(role="user", content="Return JSON."),))

    response = client.chat(request)

    assert response.model == "deepseek-v4-pro"
    assert response.content == '{"ok": true}'
    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["json"]["model"] == "deepseek-v4-pro"
    assert captured["json"]["response_format"] == {"type": "json_object"}
