import asyncio
import json
from pathlib import Path

import pytest

from app.core.errors import ContractError
from app.api.routes_rag import ingest_rag_document_api, search_rag_documents_api
from app.core.rag_document_pipeline import (
    RAG_EMBEDDING_DIMENSIONS,
    build_hash_embedding,
    build_rag_chunks,
    build_uploaded_rag_context_pack,
    ingest_uploaded_document,
    search_uploaded_documents,
    sanitize_upload_filename,
    verify_rag_round_trip_query,
)


def test_rag_ingests_uploaded_markdown_into_chunks_and_embeddings(tmp_path: Path) -> None:
    content = ("# Manual defensivo\n\n" + "LaIA usa RAG local con evidencia trazable. " * 80).encode("utf-8")

    result = ingest_uploaded_document("../Manual Defensivo.md", content, output_dir=tmp_path, max_chars=420, overlap=40)

    assert result.filename == "Manual-Defensivo.md"
    assert result.chunk_count > 1
    assert result.embedding_count == result.chunk_count
    assert result.external_network_used is False
    assert result.model_download_performed is False

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    chunks = [json.loads(line) for line in (result.output_dir / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    embeddings = [json.loads(line) for line in (result.output_dir / "embeddings.jsonl").read_text(encoding="utf-8").splitlines()]

    assert manifest["training_performed"] is False
    assert manifest["external_network_used"] is False
    assert manifest["embedding_model"] == "ojo-hash-bow-v1"
    assert len(chunks) == len(embeddings) == result.chunk_count
    assert all(row["chunk_id"].startswith(result.document_id) for row in chunks)
    assert all(len(row["vector"]) == RAG_EMBEDDING_DIMENSIONS for row in embeddings)
    assert all(row["model_download_performed"] is False for row in embeddings)


def test_rag_json_upload_is_canonicalized_before_chunking(tmp_path: Path) -> None:
    payload = b'{"z": 1, "a": {"modo": "solo lectura", "rag": true}}'

    result = ingest_uploaded_document("context.json", payload, output_dir=tmp_path)
    source = (result.output_dir / "source.txt").read_text(encoding="utf-8")

    assert '"a"' in source.splitlines()[1]
    assert '"z"' in source
    assert result.chunk_count == 1


def test_hash_embedding_is_deterministic_normalized_and_local() -> None:
    first = build_hash_embedding("LaIA RAG local local")
    second = build_hash_embedding("LaIA RAG local local")

    assert first == second
    assert len(first) == RAG_EMBEDDING_DIMENSIONS
    assert any(value != 0 for value in first)
    assert abs(sum(value * value for value in first) - 1.0) < 0.000001


def test_rag_rejects_unsupported_secret_or_tiny_uploads(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="unsupported RAG document extension"):
        sanitize_upload_filename("payload.exe")
    with pytest.raises(ContractError, match="appears to contain secrets"):
        ingest_uploaded_document("notes.md", b"api_key=supersecretvalue\ncontenido suficiente", output_dir=tmp_path)
    with pytest.raises(ContractError, match="enough text"):
        ingest_uploaded_document("notes.md", b"short", output_dir=tmp_path)


def test_rag_chunk_contract_rejects_invalid_window() -> None:
    with pytest.raises(ContractError, match="max_chars"):
        build_rag_chunks("rag-doc", "texto defensivo suficiente" * 20, max_chars=100, overlap=0)
    with pytest.raises(ContractError, match="overlap"):
        build_rag_chunks("rag-doc", "texto defensivo suficiente" * 20, max_chars=240, overlap=240)


def test_rag_upload_api_invokes_local_ingestion(monkeypatch) -> None:
    captured = {}

    class _Upload:
        filename = "upload.md"

        async def read(self) -> bytes:
            return b"Contenido defensivo para RAG local y chunking real."

    def fake_ingest(filename, data):
        captured["filename"] = filename
        captured["data"] = data

        class _Result:
            def to_dict(self):
                return {"document_id": "rag-test", "chunk_count": 1, "embedding_count": 1}

        return _Result()

    monkeypatch.setattr("app.api.routes_rag.ingest_uploaded_document", fake_ingest)

    response = asyncio.run(ingest_rag_document_api(_Upload()))

    assert captured == {"filename": "upload.md", "data": b"Contenido defensivo para RAG local y chunking real."}
    assert response["rag_document"]["document_id"] == "rag-test"


def test_uploaded_rag_semantic_search_and_context_pack_use_stored_embeddings(tmp_path: Path) -> None:
    ingest_uploaded_document("rbac.md", b"Kubernetes RBAC auditoria defensiva permisos anonimos cluster role", output_dir=tmp_path)
    ingest_uploaded_document("cloud.md", b"Inventario cloud bucket publico postura solo lectura", output_dir=tmp_path)

    search = search_uploaded_documents("kubernetes permisos rbac", output_dir=tmp_path, limit=1)
    context_pack = build_uploaded_rag_context_pack("bucket publico", output_dir=tmp_path, limit=2)

    assert search["mode"] == "local_uploaded_rag_semantic_search"
    assert search["external_network_used"] is False
    assert search["model_download_performed"] is False
    assert search["result_count"] == 1
    assert search["results"][0]["filename"] == "rbac.md"
    assert context_pack["pack_type"] == "uploaded_document_rag_context_pack"
    assert context_pack["external_ai_call_performed"] is False
    assert context_pack["result_count"] >= 1


def test_rag_search_api_returns_local_embedding_results(monkeypatch) -> None:
    def fake_search(query, limit=5):
        return {"query": query, "limit": limit, "result_count": 0, "external_network_used": False}

    monkeypatch.setattr("app.api.routes_rag.search_uploaded_documents", fake_search)

    response = search_rag_documents_api("laia", limit=3)

    assert response["search"] == {"query": "laia", "limit": 3, "result_count": 0, "external_network_used": False}


def test_rag_round_trip_verification_persists_searches_and_packs_context(tmp_path: Path) -> None:
    payload = (
        "# Runbook defensivo RAG\n\n"
        "La consulta de ida y vuelta debe recuperar controles Kubernetes RBAC, "
        "evidencia local y permisos anonimos en modo solo lectura. " * 12
    ).encode("utf-8")

    result = verify_rag_round_trip_query(
        "runbook-rbac.md",
        payload,
        "controles kubernetes rbac permisos anonimos",
        output_dir=tmp_path,
        max_chars=360,
        overlap=40,
        limit=3,
    )

    assert result["mode"] == "local_uploaded_rag_round_trip_verification"
    assert result["round_trip_verified"] is True
    assert result["external_network_used"] is False
    assert result["model_download_performed"] is False
    assert result["training_performed"] is False
    assert result["module_execution_performed"] is False
    assert result["ingestion"]["chunk_count"] >= 1
    assert result["ingestion"]["embedding_count"] == result["ingestion"]["chunk_count"]
    assert result["search"]["result_count"] >= 1
    assert result["context_pack"]["result_count"] == result["search"]["result_count"]
    assert "Kubernetes RBAC" in result["context_pack"]["results"][0]["snippet"]


def test_rag_search_api_rejects_empty_queries() -> None:
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as error:
        search_rag_documents_api("   ", limit=1)

    assert error.value.status_code == 400
    assert "query cannot be empty" in str(error.value.detail)
