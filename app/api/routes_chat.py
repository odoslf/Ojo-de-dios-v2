"""LaIA chat API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.ai.laia_chat import LaiaChatClient, create_default_laia_chat_client, run_laia_chat
from app.core.errors import ConfigurationError, ContractError

router = APIRouter()


class ChatMessagePayload(BaseModel):
    role: str = Field(..., min_length=1, max_length=16)
    content: str = Field(..., min_length=1, max_length=8_000)


class LaiaChatRequestPayload(BaseModel):
    messages: list[ChatMessagePayload] = Field(..., min_length=1, max_length=24)
    context: dict[str, Any] | str | None = None
    use_uploaded_rag: bool = False
    rag_query: str | None = Field(default=None, max_length=1_000)
    execute_local_ai: bool = False


def get_laia_chat_client() -> LaiaChatClient:
    """Return the configured local LaIA/Mistral client."""
    return create_default_laia_chat_client()


@router.post("/api/ai/laia/chat")
def run_laia_chat_api(
    payload: LaiaChatRequestPayload,
    client: LaiaChatClient = Depends(get_laia_chat_client),
) -> dict[str, Any]:
    """Run a local LaIA chat turn without executing modules or attack logic."""
    if payload.execute_local_ai is not True:
        raise HTTPException(status_code=400, detail="LaIA chat requires execute_local_ai=true.")
    try:
        messages = [message.model_dump() for message in payload.messages]
        return {
            "chat": run_laia_chat(
                messages,
                client=client,
                context=payload.context,
                use_uploaded_rag=payload.use_uploaded_rag,
                rag_query=payload.rag_query,
            )
        }
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
