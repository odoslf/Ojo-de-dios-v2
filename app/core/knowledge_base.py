"""Build the local Ojo de Dios knowledge base artifacts.

The default mode is dependency-free and deterministic: it reads approved project
sources, chunks them, and writes JSON/JSONL artifacts that LaIA/Hermes can use as
an auditable context pack. Semantic Chroma generation is optional and only runs
when explicitly requested and the optional packages are already available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

READY_DOCS_ONLY = "READY_DOCS_ONLY"
READY_RAG = "READY_RAG"
FAILED = "FAILED"
DEFAULT_KNOWLEDGE_DIR = Path("storage/knowledge")
KNOWLEDGE_CONTEXT_PACK_TYPE = "knowledge_search_context_pack"
KNOWLEDGE_CONTEXT_SCHEMA_VERSION = 1

DEFAULT_MAX_CHARS = 1800
DEFAULT_OVERLAP = 180
SOURCE_EXTENSIONS = {".md", ".json", ".py", ".bat", ".example"}
EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "storage",
}
ROOT_FILES = {
    ".env.example",
    "AI_HANDOFF_OJO_DE_DIOS.md",
    "MASTER_PLAN_OJO_DE_DIOS.md",
    "README.md",
}
SOURCE_ROOTS = ("docs", "app/core", "app/contracts", "app/modules", "scripts/windows/ia")


@dataclass(frozen=True)
class SourceDocument:
    relative_path: str
    source_type: str
    sha256: str
    text: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_type_for(relative_path: str) -> str:
    if relative_path in ROOT_FILES:
        return "root_reference"
    if relative_path.startswith("docs/techniques/"):
        return "technique_guide"
    if relative_path.startswith("docs/ai_prompts/"):
        return "ai_prompt"
    if relative_path.startswith("docs/setup/"):
        return "setup_guide"
    if relative_path.endswith("module_manifest.json"):
        return "module_manifest"
    if relative_path == "app/core/module_catalog.py":
        return "module_catalog"
    if relative_path.startswith("app/contracts/"):
        return "runtime_contract"
    if relative_path.startswith("scripts/windows/ia/"):
        return "windows_ia_script"
    return "project_reference"


def should_index(path: Path, repo_root: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.relative_to(repo_root).parts):
        return False
    rel = path.relative_to(repo_root).as_posix()
    if rel in ROOT_FILES:
        return True
    if not any(rel == root or rel.startswith(f"{root}/") for root in SOURCE_ROOTS):
        return False
    if path.name == ".gitkeep":
        return False
    if path.suffix in SOURCE_EXTENSIONS:
        return True
    return path.name.endswith(".env.example")


def iter_source_paths(repo_root: Path) -> Iterable[Path]:
    for path in sorted(repo_root.rglob("*")):
        if path.is_file() and should_index(path, repo_root):
            yield path


def load_sources(repo_root: Path) -> list[SourceDocument]:
    sources: list[SourceDocument] = []
    for path in iter_source_paths(repo_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if not text.strip():
            continue
        rel = path.relative_to(repo_root).as_posix()
        sources.append(
            SourceDocument(
                relative_path=rel,
                source_type=source_type_for(rel),
                sha256=sha256_text(text),
                text=text,
            )
        )
    return sources


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS, overlap: int = DEFAULT_OVERLAP) -> list[str]:
    normalized = re.sub(r"\n{3,}", "\n\n", text.strip())
    if not normalized:
        return []
    paragraphs = re.split(r"(?<=\n)\n+", normalized)
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = current[-overlap:] if overlap > 0 else ""
        while len(paragraph) > max_chars:
            chunks.append(paragraph[:max_chars])
            paragraph = paragraph[max(1, max_chars - overlap) :]
        current = f"{current}\n\n{paragraph}".strip() if current else paragraph
    if current:
        chunks.append(current)
    return chunks


def build_keyword_index(chunks: Sequence[dict]) -> dict[str, list[str]]:
    index: dict[str, set[str]] = defaultdict(set)
    for chunk in chunks:
        tokens = set(re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{3,}", chunk["text"].lower()))
        for token in tokens:
            index[token].add(chunk["chunk_id"])
    return {token: sorted(ids) for token, ids in sorted(index.items())}


def try_build_semantic_index(chunks: Sequence[dict], output_dir: Path) -> tuple[str, str | None]:
    try:
        from langchain.schema import Document
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import Chroma
    except Exception as exc:  # pragma: no cover - depends on optional local packages
        return "MISSING_OPTIONAL_DEPENDENCY", str(exc)

    try:  # pragma: no cover - heavy optional integration
        docs = [
            Document(
                page_content=chunk["text"],
                metadata={
                    "chunk_id": chunk["chunk_id"],
                    "source_path": chunk["source_path"],
                    "source_type": chunk["source_type"],
                    "source_sha256": chunk["source_sha256"],
                },
            )
            for chunk in chunks
        ]
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=str(output_dir / "chroma"),
        )
        vectorstore.persist()
        return "READY", None
    except Exception as exc:
        return "FAILED", str(exc)


def build_knowledge_base(
    repo_root: Path,
    output_dir: Path,
    mode: str = "docs-only",
    max_chars: int = DEFAULT_MAX_CHARS,
    overlap: int = DEFAULT_OVERLAP,
) -> dict:
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    sources = load_sources(repo_root)
    chunks: list[dict] = []
    for source in sources:
        for index, chunk in enumerate(chunk_text(source.text, max_chars=max_chars, overlap=overlap), start=1):
            chunks.append(
                {
                    "chunk_id": f"kb-{len(chunks) + 1:06d}",
                    "source_path": source.relative_path,
                    "source_type": source.source_type,
                    "source_sha256": source.sha256,
                    "chunk_index": index,
                    "text_sha256": sha256_text(chunk),
                    "text": chunk,
                }
            )

    semantic_status = "SKIPPED"
    semantic_error = None
    if mode == "semantic" and chunks:
        semantic_status, semantic_error = try_build_semantic_index(chunks, output_dir)

    status_name = READY_RAG if semantic_status == "READY" else READY_DOCS_ONLY
    if not sources or not chunks:
        status_name = FAILED

    manifest = {
        "schema_version": 1,
        "created_at": utc_now_iso(),
        "repo_root_name": repo_root.name,
        "source_count": len(sources),
        "sources": [
            {
                "path": source.relative_path,
                "type": source.source_type,
                "sha256": source.sha256,
                "character_count": len(source.text),
            }
            for source in sources
        ],
    }
    chunks_path = output_dir / "chunks.jsonl"
    chunks_path.write_text("\n".join(json.dumps(chunk, ensure_ascii=False) for chunk in chunks) + ("\n" if chunks else ""), encoding="utf-8")
    write_json(output_dir / "source_manifest.json", manifest)
    write_json(output_dir / "keyword_index.json", build_keyword_index(chunks))

    status = {
        "schema_version": 1,
        "created_at": utc_now_iso(),
        "status": status_name,
        "requested_mode": mode,
        "semantic_index_status": semantic_status,
        "semantic_index_error": semantic_error,
        "external_network_used": False,
        "source_count": len(sources),
        "chunk_count": len(chunks),
        "artifacts": [
            "storage/knowledge/source_manifest.json",
            "storage/knowledge/chunks.jsonl",
            "storage/knowledge/keyword_index.json",
            "storage/knowledge/knowledge_status.json",
        ],
    }
    write_json(output_dir / "knowledge_status.json", status)
    return status


def resolve_knowledge_dir(repo_root: Path, output_dir: Path | None = None) -> Path:
    """Return the concrete storage path for local knowledge artifacts."""
    if output_dir is None:
        output_dir = DEFAULT_KNOWLEDGE_DIR
    return output_dir if output_dir.is_absolute() else repo_root / output_dir


def read_knowledge_status(repo_root: Path = Path.cwd(), output_dir: Path | None = None) -> dict:
    """Read the auditable local knowledge status manifest."""
    knowledge_dir = resolve_knowledge_dir(repo_root.resolve(), output_dir)
    status_path = knowledge_dir / "knowledge_status.json"
    if not status_path.is_file():
        raise FileNotFoundError(status_path)
    return json.loads(status_path.read_text(encoding="utf-8"))


def iter_knowledge_chunks(repo_root: Path = Path.cwd(), output_dir: Path | None = None) -> Iterable[dict]:
    """Yield indexed knowledge chunks from the local JSONL artifact."""
    knowledge_dir = resolve_knowledge_dir(repo_root.resolve(), output_dir)
    chunks_path = knowledge_dir / "chunks.jsonl"
    if not chunks_path.is_file():
        raise FileNotFoundError(chunks_path)
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def search_knowledge_base(
    query: str,
    repo_root: Path = Path.cwd(),
    output_dir: Path | None = None,
    limit: int = 5,
) -> dict:
    """Search the local docs-only knowledge index with deterministic lexical scoring."""
    normalized_query = query.strip().lower()
    if not normalized_query:
        raise ValueError("Knowledge search query must not be empty.")
    if limit < 1:
        raise ValueError("Knowledge search limit must be greater than zero.")

    tokens = set(re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_\-]{3,}", normalized_query))
    if not tokens:
        raise ValueError("Knowledge search query must contain at least one searchable token.")

    status = read_knowledge_status(repo_root=repo_root, output_dir=output_dir)
    results: list[dict] = []
    for chunk in iter_knowledge_chunks(repo_root=repo_root, output_dir=output_dir):
        text = str(chunk.get("text", ""))
        searchable = text.lower()
        matched_tokens = sorted(token for token in tokens if token in searchable)
        if not matched_tokens:
            continue
        first_position = min(searchable.find(token) for token in matched_tokens if searchable.find(token) >= 0)
        snippet_start = max(0, first_position - 120)
        snippet_end = min(len(text), first_position + 360)
        results.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "source_path": chunk.get("source_path"),
                "source_type": chunk.get("source_type"),
                "source_sha256": chunk.get("source_sha256"),
                "matched_tokens": matched_tokens,
                "score": len(matched_tokens),
                "snippet": text[snippet_start:snippet_end].strip(),
            }
        )
    results.sort(key=lambda item: (-int(item["score"]), str(item["source_path"]), str(item["chunk_id"])))
    return {
        "query": query,
        "limit": limit,
        "knowledge_status": status.get("status"),
        "semantic_index_status": status.get("semantic_index_status"),
        "results": results[:limit],
        "count": len(results[:limit]),
        "total_matches": len(results),
    }


def build_knowledge_context_pack(
    query: str,
    repo_root: Path = Path.cwd(),
    output_dir: Path | None = None,
    limit: int = 5,
) -> dict:
    """Build a bounded context pack from local knowledge search results."""
    search = search_knowledge_base(query=query, repo_root=repo_root, output_dir=output_dir, limit=limit)
    return {
        "schema_version": KNOWLEDGE_CONTEXT_SCHEMA_VERSION,
        "pack_type": KNOWLEDGE_CONTEXT_PACK_TYPE,
        "mode": "local_knowledge_search_no_ai",
        "query": search["query"],
        "knowledge_status": search["knowledge_status"],
        "semantic_index_status": search["semantic_index_status"],
        "result_count": search["count"],
        "total_matches": search["total_matches"],
        "results": search["results"],
        "external_ai_call_performed": False,
        "model_download_performed": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Ojo de Dios local knowledge artifacts.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_KNOWLEDGE_DIR)
    parser.add_argument("--mode", choices=("docs-only", "semantic"), default="docs-only")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = args.output_dir if args.output_dir.is_absolute() else args.repo_root / args.output_dir
    status = build_knowledge_base(
        repo_root=args.repo_root,
        output_dir=output_dir,
        mode=args.mode,
        max_chars=args.max_chars,
        overlap=args.overlap,
    )
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status["status"] in {READY_DOCS_ONLY, READY_RAG} else 1


if __name__ == "__main__":
    raise SystemExit(main())
