"""Contracts for the local knowledge-base builder."""

import json
from pathlib import Path

from app.core import knowledge_base as builder


def create_minimal_repo(root: Path) -> None:
    (root / "docs" / "techniques").mkdir(parents=True)
    (root / "app" / "core").mkdir(parents=True)
    (root / "app" / "modules" / "m01_osint").mkdir(parents=True)
    (root / "scripts" / "windows" / "ia").mkdir(parents=True)
    (root / "README.md").write_text("# Ojo de Dios\n\nGuia principal.", encoding="utf-8")
    (root / ".env.example").write_text("MISTRAL_MODEL=CognitiveComputations/dolphin-mistral-nemo:12b\n", encoding="utf-8")
    (root / "docs" / "techniques" / "01_OSINT.md").write_text("# OSINT\n\nContenido operativo autorizado.", encoding="utf-8")
    (root / "app" / "core" / "module_catalog.py").write_text("MODULES = []\n", encoding="utf-8")
    (root / "app" / "modules" / "m01_osint" / "module_manifest.json").write_text('{"id":"m01_osint"}\n', encoding="utf-8")
    (root / "storage" / "knowledge").mkdir(parents=True)
    (root / "storage" / "knowledge" / "old.tmp").write_text("no indexar storage", encoding="utf-8")


def test_docs_only_builder_writes_auditable_artifacts_without_optional_dependencies(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)

    output_dir = tmp_path / "storage" / "knowledge"
    status = builder.build_knowledge_base(tmp_path, output_dir, mode="docs-only", max_chars=120, overlap=12)

    assert status["status"] == "READY_DOCS_ONLY"
    assert status["semantic_index_status"] == "SKIPPED"
    assert status["external_network_used"] is False
    assert status["source_count"] >= 4
    assert status["chunk_count"] >= 4

    manifest = json.loads((output_dir / "source_manifest.json").read_text(encoding="utf-8"))
    source_paths = {source["path"] for source in manifest["sources"]}
    assert "README.md" in source_paths
    assert ".env.example" in source_paths
    assert "docs/techniques/01_OSINT.md" in source_paths
    assert "storage/knowledge/old.tmp" not in source_paths

    chunks = [json.loads(line) for line in (output_dir / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
    assert chunks
    assert all(chunk["source_sha256"] for chunk in chunks)
    assert all(chunk["chunk_id"].startswith("kb-") for chunk in chunks)
    assert (output_dir / "keyword_index.json").is_file()


def test_builder_cli_returns_success_for_docs_only_mode(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)

    rc = builder.main([
        "--repo-root",
        str(tmp_path),
        "--output-dir",
        str(tmp_path / "storage" / "knowledge"),
        "--mode",
        "docs-only",
    ])

    assert rc == 0
    status = json.loads((tmp_path / "storage" / "knowledge" / "knowledge_status.json").read_text(encoding="utf-8"))
    assert status["status"] == "READY_DOCS_ONLY"


def test_knowledge_search_uses_local_chunks_without_ai_or_network(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)
    output_dir = tmp_path / "storage" / "knowledge"
    builder.build_knowledge_base(tmp_path, output_dir, mode="docs-only", max_chars=120, overlap=12)

    payload = builder.search_knowledge_base("mistral osint", repo_root=tmp_path, output_dir=output_dir, limit=3)

    assert payload["knowledge_status"] == "READY_DOCS_ONLY"
    assert payload["count"] >= 1
    assert payload["results"][0]["source_path"] in {".env.example", "docs/techniques/01_OSINT.md"}


def test_knowledge_context_pack_is_prompt_safe_and_local(tmp_path: Path) -> None:
    create_minimal_repo(tmp_path)
    output_dir = tmp_path / "storage" / "knowledge"
    builder.build_knowledge_base(tmp_path, output_dir, mode="docs-only", max_chars=120, overlap=12)

    context_pack = builder.build_knowledge_context_pack(
        "mistral osint",
        repo_root=tmp_path,
        output_dir=output_dir,
        limit=2,
    )

    assert context_pack["pack_type"] == "knowledge_search_context_pack"
    assert context_pack["mode"] == "local_knowledge_search_no_ai"
    assert context_pack["external_ai_call_performed"] is False
    assert context_pack["model_download_performed"] is False
    assert context_pack["result_count"] >= 1
