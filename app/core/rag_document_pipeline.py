"""Local RAG ingestion pipeline for operator-uploaded documents.

The pipeline is dependency-free and local-only for R23: it validates uploaded
bytes, extracts text from safe document formats, chunks text deterministically,
creates deterministic hashed embeddings, and writes auditable JSON/JSONL
artifacts.  It does not train models, download embeddings, call external APIs or
ingest secrets.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from app.core.errors import ContractError
from app.core.knowledge_base import chunk_text, sha256_text, write_json

RAG_DOCUMENT_SCHEMA_VERSION = 1
RAG_EMBEDDING_DIMENSIONS = 128
RAG_MAX_UPLOAD_BYTES = 2_000_000
RAG_DEFAULT_CHUNK_CHARS = 1_200
RAG_DEFAULT_CHUNK_OVERLAP = 120
RAG_ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".csv"}
RAG_DEFAULT_OUTPUT_DIR = Path("storage/rag/documents")
_SECRET_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|authorization|bearer|client[_-]?secret|password|private[_-]?key|secret|token)\b\s*[:=]"
)
_TOKEN_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{2,}")
_SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True, slots=True)
class RagDocumentChunk:
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    text_sha256: str
    token_count: int


@dataclass(frozen=True, slots=True)
class RagIngestionResult:
    document_id: str
    filename: str
    source_sha256: str
    chunk_count: int
    embedding_count: int
    output_dir: Path
    manifest_path: Path
    external_network_used: bool = False
    model_download_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": RAG_DOCUMENT_SCHEMA_VERSION,
            "document_id": self.document_id,
            "filename": self.filename,
            "source_sha256": self.source_sha256,
            "chunk_count": self.chunk_count,
            "embedding_count": self.embedding_count,
            "output_dir": str(self.output_dir),
            "manifest_path": str(self.manifest_path),
            "external_network_used": self.external_network_used,
            "model_download_performed": self.model_download_performed,
        }


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def sanitize_upload_filename(filename: str) -> str:
    """Return a safe basename for an uploaded document."""
    raw = Path(str(filename or "")).name.strip()
    if not raw:
        raise ContractError("filename is required.")
    safe = _SAFE_FILENAME_PATTERN.sub("-", raw).strip(".-_")
    if not safe:
        raise ContractError("filename does not contain a usable name.")
    suffix = Path(safe).suffix.casefold()
    if suffix not in RAG_ALLOWED_EXTENSIONS:
        raise ContractError(f"unsupported RAG document extension: {suffix or '<none>'}")
    return safe[:160]


def _decode_upload(data: bytes) -> str:
    if not data:
        raise ContractError("uploaded document is empty.")
    if len(data) > RAG_MAX_UPLOAD_BYTES:
        raise ContractError(f"uploaded document exceeds {RAG_MAX_UPLOAD_BYTES} bytes.")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("uploaded document must be UTF-8 text for this RAG base pipeline.") from error


def _extract_text(filename: str, text: str) -> str:
    suffix = Path(filename).suffix.casefold()
    if suffix == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise ContractError("JSON document is not valid JSON.") from error
        return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    return text.replace("\x00", "").strip()


def validate_rag_document_text(text: str) -> str:
    """Reject unusable or sensitive-looking uploaded RAG text."""
    normalized = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(normalized) < 8:
        raise ContractError("uploaded document does not contain enough text to index.")
    if _SECRET_PATTERN.search(normalized):
        raise ContractError("uploaded document appears to contain secrets and cannot be indexed.")
    return normalized


def tokenize_for_embedding(text: str) -> list[str]:
    """Tokenize text for deterministic local hashed embeddings."""
    return [match.group(0).casefold() for match in _TOKEN_PATTERN.finditer(text)]


def build_hash_embedding(text: str, dimensions: int = RAG_EMBEDDING_DIMENSIONS) -> list[float]:
    """Build a deterministic unit-normalized hashed bag-of-words embedding."""
    if dimensions < 8:
        raise ContractError("embedding dimensions must be at least 8.")
    vector = [0.0] * dimensions
    counts = Counter(tokenize_for_embedding(text))
    for token, count in counts.items():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign * (1.0 + math.log(count))
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 8) for value in vector]


def make_document_id(filename: str, source_sha256: str) -> str:
    """Create a stable document id from filename and content hash."""
    stem = Path(filename).stem[:48].lower() or "document"
    stem = _SAFE_FILENAME_PATTERN.sub("-", stem).strip("-") or "document"
    digest = hashlib.sha256(f"{filename}\n{source_sha256}".encode("utf-8")).hexdigest()[:16]
    return f"rag-{stem}-{digest}"


def build_rag_chunks(document_id: str, text: str, *, max_chars: int = RAG_DEFAULT_CHUNK_CHARS, overlap: int = RAG_DEFAULT_CHUNK_OVERLAP) -> list[RagDocumentChunk]:
    """Chunk one uploaded document for RAG ingestion."""
    if max_chars < 200:
        raise ContractError("max_chars must be at least 200.")
    if overlap < 0 or overlap >= max_chars:
        raise ContractError("overlap must be non-negative and smaller than max_chars.")
    chunks: list[RagDocumentChunk] = []
    for index, chunk in enumerate(chunk_text(text, max_chars=max_chars, overlap=overlap), start=1):
        chunks.append(
            RagDocumentChunk(
                chunk_id=f"{document_id}-chunk-{index:04d}",
                document_id=document_id,
                chunk_index=index,
                text=chunk,
                text_sha256=sha256_text(chunk),
                token_count=len(tokenize_for_embedding(chunk)),
            )
        )
    if not chunks:
        raise ContractError("uploaded document produced no chunks.")
    return chunks


def _jsonl(rows: Iterable[dict[str, Any]]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n"


def ingest_uploaded_document(
    filename: str,
    data: bytes,
    *,
    output_dir: Path | None = None,
    max_chars: int = RAG_DEFAULT_CHUNK_CHARS,
    overlap: int = RAG_DEFAULT_CHUNK_OVERLAP,
) -> RagIngestionResult:
    """Ingest one uploaded document into local RAG chunk and embedding artifacts."""
    safe_filename = sanitize_upload_filename(filename)
    raw_text = _decode_upload(data)
    extracted_text = validate_rag_document_text(_extract_text(safe_filename, raw_text))
    source_sha256 = hashlib.sha256(data).hexdigest()
    document_id = make_document_id(safe_filename, source_sha256)
    root = (output_dir or RAG_DEFAULT_OUTPUT_DIR).resolve()
    document_dir = root / document_id
    document_dir.mkdir(parents=True, exist_ok=True)

    chunks = build_rag_chunks(document_id, extracted_text, max_chars=max_chars, overlap=overlap)
    embedding_rows = [
        {
            "schema_version": RAG_DOCUMENT_SCHEMA_VERSION,
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "embedding_model": "ojo-hash-bow-v1",
            "dimensions": RAG_EMBEDDING_DIMENSIONS,
            "vector": build_hash_embedding(chunk.text),
            "external_network_used": False,
            "model_download_performed": False,
        }
        for chunk in chunks
    ]
    chunk_rows = [
        {
            "schema_version": RAG_DOCUMENT_SCHEMA_VERSION,
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "text_sha256": chunk.text_sha256,
            "token_count": chunk.token_count,
            "text": chunk.text,
        }
        for chunk in chunks
    ]
    (document_dir / "source.txt").write_text(extracted_text + "\n", encoding="utf-8")
    (document_dir / "chunks.jsonl").write_text(_jsonl(chunk_rows), encoding="utf-8")
    (document_dir / "embeddings.jsonl").write_text(_jsonl(embedding_rows), encoding="utf-8")
    manifest = {
        "schema_version": RAG_DOCUMENT_SCHEMA_VERSION,
        "created_at": utc_now_iso(),
        "document_id": document_id,
        "filename": safe_filename,
        "source_sha256": source_sha256,
        "source_text_sha256": sha256_text(extracted_text),
        "chunk_count": len(chunks),
        "embedding_count": len(embedding_rows),
        "embedding_model": "ojo-hash-bow-v1",
        "embedding_dimensions": RAG_EMBEDDING_DIMENSIONS,
        "artifacts": ["source.txt", "chunks.jsonl", "embeddings.jsonl", "manifest.json"],
        "external_network_used": False,
        "model_download_performed": False,
        "training_performed": False,
    }
    manifest_path = document_dir / "manifest.json"
    write_json(manifest_path, manifest)
    return RagIngestionResult(
        document_id=document_id,
        filename=safe_filename,
        source_sha256=source_sha256,
        chunk_count=len(chunks),
        embedding_count=len(embedding_rows),
        output_dir=document_dir,
        manifest_path=manifest_path,
    )


def iter_rag_document_chunks(*, output_dir: Path | None = None) -> Iterable[dict[str, Any]]:
    """Yield uploaded RAG chunks joined with their stored embeddings."""
    root = (output_dir or RAG_DEFAULT_OUTPUT_DIR).resolve()
    if not root.exists():
        return
    for document_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        manifest_path = document_dir / "manifest.json"
        chunks_path = document_dir / "chunks.jsonl"
        embeddings_path = document_dir / "embeddings.jsonl"
        if not manifest_path.is_file() or not chunks_path.is_file() or not embeddings_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            chunks = [json.loads(line) for line in chunks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            embeddings = [json.loads(line) for line in embeddings_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        except (OSError, json.JSONDecodeError):
            continue
        embeddings_by_chunk = {str(row.get("chunk_id")): row for row in embeddings if isinstance(row, dict)}
        for chunk in chunks:
            if not isinstance(chunk, dict):
                continue
            embedding = embeddings_by_chunk.get(str(chunk.get("chunk_id")))
            vector = embedding.get("vector") if isinstance(embedding, dict) else None
            if not isinstance(vector, list):
                continue
            yield {
                "document_id": manifest.get("document_id"),
                "filename": manifest.get("filename"),
                "source_sha256": manifest.get("source_sha256"),
                "chunk_id": chunk.get("chunk_id"),
                "chunk_index": chunk.get("chunk_index"),
                "text_sha256": chunk.get("text_sha256"),
                "text": chunk.get("text", ""),
                "embedding_model": embedding.get("embedding_model"),
                "vector": [float(value) for value in vector],
            }


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return cosine similarity for two numeric vectors."""
    if len(left) != len(right):
        raise ContractError("vectors must have the same dimensions.")
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def search_uploaded_documents(query: str, *, output_dir: Path | None = None, limit: int = 5) -> dict[str, Any]:
    """Search uploaded RAG document chunks using deterministic local embeddings."""
    normalized_query = str(query or "").strip()
    if not normalized_query:
        raise ContractError("RAG search query cannot be empty.")
    if limit < 1:
        raise ContractError("RAG search limit must be greater than zero.")
    query_vector = build_hash_embedding(normalized_query)
    results: list[dict[str, Any]] = []
    for row in iter_rag_document_chunks(output_dir=output_dir):
        score = cosine_similarity(query_vector, row["vector"])
        if score <= 0:
            continue
        text = str(row.get("text") or "")
        results.append({
            "document_id": row.get("document_id"),
            "filename": row.get("filename"),
            "source_sha256": row.get("source_sha256"),
            "chunk_id": row.get("chunk_id"),
            "chunk_index": row.get("chunk_index"),
            "text_sha256": row.get("text_sha256"),
            "embedding_model": row.get("embedding_model"),
            "score": round(score, 8),
            "snippet": text[:900],
        })
    results.sort(key=lambda item: (-float(item["score"]), str(item["filename"]), str(item["chunk_id"])))
    limited = results[:limit]
    return {
        "schema_version": RAG_DOCUMENT_SCHEMA_VERSION,
        "mode": "local_uploaded_rag_semantic_search",
        "query": normalized_query,
        "embedding_model": "ojo-hash-bow-v1",
        "result_count": len(limited),
        "total_matches": len(results),
        "results": limited,
        "external_network_used": False,
        "model_download_performed": False,
    }


def build_uploaded_rag_context_pack(query: str, *, output_dir: Path | None = None, limit: int = 4) -> dict[str, Any]:
    """Build a prompt-safe context pack from uploaded document semantic search."""
    search = search_uploaded_documents(query, output_dir=output_dir, limit=limit)
    return {
        "schema_version": RAG_DOCUMENT_SCHEMA_VERSION,
        "pack_type": "uploaded_document_rag_context_pack",
        "mode": "local_uploaded_rag_context_no_external_ai",
        "query": search["query"],
        "result_count": search["result_count"],
        "total_matches": search["total_matches"],
        "results": search["results"],
        "external_ai_call_performed": False,
        "external_network_used": False,
        "model_download_performed": False,
    }


def verify_rag_round_trip_query(
    filename: str,
    data: bytes,
    query: str,
    *,
    output_dir: Path | None = None,
    max_chars: int = RAG_DEFAULT_CHUNK_CHARS,
    overlap: int = RAG_DEFAULT_CHUNK_OVERLAP,
    limit: int = 4,
) -> dict[str, Any]:
    """Ingest one upload, search it, and build the LaIA-ready local RAG context pack.

    This is the R25 verification path: it performs the full local round trip
    against persisted artifacts instead of in-memory placeholders.  It remains
    dependency-free and records explicit negative flags for network/model
    downloads/training so callers can audit the run.
    """
    ingestion = ingest_uploaded_document(
        filename,
        data,
        output_dir=output_dir,
        max_chars=max_chars,
        overlap=overlap,
    )
    search = search_uploaded_documents(query, output_dir=output_dir, limit=limit)
    context_pack = build_uploaded_rag_context_pack(query, output_dir=output_dir, limit=limit)
    return {
        "schema_version": RAG_DOCUMENT_SCHEMA_VERSION,
        "mode": "local_uploaded_rag_round_trip_verification",
        "round_trip_verified": bool(
            ingestion.chunk_count
            and ingestion.embedding_count == ingestion.chunk_count
            and search["result_count"] > 0
            and context_pack["result_count"] > 0
        ),
        "query": search["query"],
        "ingestion": ingestion.to_dict(),
        "search": search,
        "context_pack": context_pack,
        "external_network_used": False,
        "model_download_performed": False,
        "training_performed": False,
        "module_execution_performed": False,
    }
