"""Hermes DeepSeek assist service contract tests."""

import json

import pytest

from app.ai.deepseek_client import DeepSeekChatResponse
from app.ai.hermes_assist import (
    HERMES_ASSIST_MODE,
    HermesAssistRequest,
    HermesDeepSeekAssistService,
    build_hermes_deepseek_chat_request,
)
from app.config import Settings
from app.core.errors import ConfigurationError, ContractError


class _FakeHermesClient:
    def __init__(self):
        self.requests = []

    def chat(self, request):
        self.requests.append(request)
        return DeepSeekChatResponse(
            model=request.model,
            content='{"answer":"ok","execution_implied":false}',
            raw={"id": "chatcmpl-test"},
        )


def test_build_hermes_request_is_json_only_and_non_executing() -> None:
    settings = Settings(_env_file=None)
    request = HermesAssistRequest(question="How should Hermes prepare a parser?", context={"module_id": "m16_ops_quality"})

    chat_request = build_hermes_deepseek_chat_request(request, settings)
    user_payload = json.loads(chat_request.messages[1].content)

    assert chat_request.model == "deepseek-v4-pro"
    assert chat_request.json_mode is True
    assert chat_request.thinking_enabled is False
    assert chat_request.reasoning_effort == "low"
    assert "Do not execute tools" in chat_request.messages[0].content
    assert user_payload["required_output"]["execution_implied"] is False


def test_hermes_request_rejects_pro_model_without_approval() -> None:
    settings = Settings(_env_file=None, deepseek_model="deepseek-v4-flash")
    request = HermesAssistRequest(
        question="Use pro?",
        context={},
        model="deepseek-v4-pro",
        allow_pro_model=False,
    )

    with pytest.raises(ContractError, match="pro model requires explicit approval"):
        build_hermes_deepseek_chat_request(request, settings)


def test_hermes_request_accepts_pro_model_with_explicit_approval() -> None:
    settings = Settings(_env_file=None)
    request = HermesAssistRequest(
        question="Use pro with approval?",
        context={},
        model="deepseek-v4-pro",
        allow_pro_model=True,
        reasoning_effort="medium",
    )

    chat_request = build_hermes_deepseek_chat_request(request, settings)

    assert chat_request.model == "deepseek-v4-pro"
    assert chat_request.reasoning_effort == "medium"


def test_hermes_service_refuses_external_call_when_disabled() -> None:
    service = HermesDeepSeekAssistService(Settings(_env_file=None), client=_FakeHermesClient())

    with pytest.raises(ConfigurationError, match="disabled"):
        service.ask_json(HermesAssistRequest(question="hello", context={}))


def test_hermes_service_calls_client_when_enabled_and_key_present() -> None:
    client = _FakeHermesClient()
    settings = Settings(_env_file=None, ai_enabled=True, angel_enabled=True, deepseek_api_key="secret")
    service = HermesDeepSeekAssistService(settings, client=client)

    response = service.ask_json(HermesAssistRequest(question="hello", context={"safe": True}))

    assert response.mode == HERMES_ASSIST_MODE
    assert response.external_ai_call_performed is True
    assert response.content == '{"answer":"ok","execution_implied":false}'
    assert len(client.requests) == 1
    assert client.requests[0].model == "deepseek-v4-pro"
