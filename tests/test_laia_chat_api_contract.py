import pytest
from fastapi import HTTPException

from app.ai.laia_chat import build_laia_chat_prompt, normalize_chat_messages, run_laia_chat
from app.api.routes_chat import ChatMessagePayload, LaiaChatRequestPayload, run_laia_chat_api
from app.config import Settings
from app.core.errors import ContractError


class _FakeLaiaClient:
    model = "CognitiveComputations/dolphin-mistral-nemo:12b"

    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "Respuesta segura token=supersecret"


def test_laia_chat_prompt_is_bounded_chatml_without_module_execution(tmp_path) -> None:
    prompt_path = tmp_path / "docs" / "ai_prompts" / "laia_mistral_system_prompt.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Sistema LaIA local", encoding="utf-8")
    settings = Settings(_env_file=None, mistral_system_prompt_path="docs/ai_prompts/laia_mistral_system_prompt.md")
    messages = normalize_chat_messages([{"role": "user", "content": "Hola authorization=secret123"}])

    prompt = build_laia_chat_prompt(messages, settings=settings, context={"module": "m01"}, repo_root=tmp_path)

    assert prompt["mode"] == "laia_local_mistral_chat"
    assert prompt["module_execution_performed"] is False
    assert prompt["external_ai_call_performed"] is False
    assert len(prompt["prompt_sha256"]) == 64
    assert "Sistema LaIA local" in prompt["prompt"]
    assert "authorization=[REDACTED]" in prompt["prompt"]
    assert "no se ejecuta ningún módulo" in prompt["prompt"]


def test_laia_chat_runs_local_client_and_redacts_response() -> None:
    fake = _FakeLaiaClient()

    result = run_laia_chat([{"role": "user", "content": "Resume el estado"}], client=fake, context="solo lectura")

    assert result["local_ai_call_performed"] is True
    assert result["external_ai_call_performed"] is False
    assert result["module_execution_performed"] is False
    assert result["uploaded_rag_context_included"] is False
    assert result["answer"] == "Respuesta segura token=[REDACTED]"
    assert fake.prompts and "solo lectura" in fake.prompts[0]


def test_laia_chat_api_requires_explicit_local_ai_flag() -> None:
    payload = LaiaChatRequestPayload(messages=[ChatMessagePayload(role="user", content="hola")])

    with pytest.raises(HTTPException) as error:
        run_laia_chat_api(payload, client=_FakeLaiaClient())

    assert error.value.status_code == 400
    assert "execute_local_ai=true" in str(error.value.detail)


def test_laia_chat_api_passes_messages_to_local_ai_client() -> None:
    fake = _FakeLaiaClient()
    payload = LaiaChatRequestPayload(
        messages=[ChatMessagePayload(role="user", content="¿Qué puedes revisar?")],
        context={"page": "chat"},
        execute_local_ai=True,
    )

    response = run_laia_chat_api(payload, client=fake)

    assert response["chat"]["model"] == fake.model
    assert response["chat"]["local_ai_call_performed"] is True
    assert response["chat"]["module_execution_performed"] is False
    assert fake.prompts[0].startswith("<|im_start|>system")


def test_laia_chat_rejects_invalid_message_contracts() -> None:
    with pytest.raises(ContractError, match="last message"):
        normalize_chat_messages([{"role": "assistant", "content": "hola"}])
    with pytest.raises(ContractError, match="role"):
        normalize_chat_messages([{"role": "tool", "content": "hola"}])


def test_laia_chat_includes_uploaded_rag_context_when_enabled(tmp_path) -> None:
    from app.core.rag_document_pipeline import ingest_uploaded_document

    ingest_uploaded_document("manual.md", b"LaIA RAG contexto defensivo para modulos y evidencias", output_dir=tmp_path)
    fake = _FakeLaiaClient()

    result = run_laia_chat(
        [{"role": "user", "content": "Resume RAG defensivo"}],
        client=fake,
        use_uploaded_rag=True,
        rag_output_dir=tmp_path,
    )

    assert result["uploaded_rag_context_included"] is True
    assert result["uploaded_rag_result_count"] >= 1
    assert "Contexto RAG local" in fake.prompts[0]


def test_laia_chat_api_forwards_uploaded_rag_flags(monkeypatch) -> None:
    captured = {}

    def fake_run(messages, **kwargs):
        captured.update(kwargs)
        return {"answer": "ok", "uploaded_rag_context_included": kwargs["use_uploaded_rag"]}

    monkeypatch.setattr("app.api.routes_chat.run_laia_chat", fake_run)
    payload = LaiaChatRequestPayload(
        messages=[ChatMessagePayload(role="user", content="busca contexto")],
        use_uploaded_rag=True,
        rag_query="contexto",
        execute_local_ai=True,
    )

    response = run_laia_chat_api(payload, client=_FakeLaiaClient())

    assert captured["use_uploaded_rag"] is True
    assert captured["rag_query"] == "contexto"
    assert response["chat"]["uploaded_rag_context_included"] is True
