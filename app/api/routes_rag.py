"""Local RAG document ingestion API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.errors import ContractError
from app.core.rag_document_pipeline import ingest_uploaded_document, search_uploaded_documents

router = APIRouter()


@router.post("/api/rag/documents")
async def ingest_rag_document_api(file: UploadFile = File(...)) -> dict[str, Any]:
    """Ingest one uploaded document into local RAG chunks and embeddings."""
    try:
        data = await file.read()
        result = ingest_uploaded_document(file.filename or "document.txt", data)
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"rag_document": result.to_dict()}


@router.get("/api/rag/documents/search")
def search_rag_documents_api(q: str, limit: int = 5) -> dict[str, Any]:
    """Search uploaded local RAG documents using stored embeddings."""
    try:
        return {"search": search_uploaded_documents(q, limit=limit)}
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
