"""Module context packs for LaIA/Mistral assisted module views.

This module builds deterministic, JSON-safe context from the authoritative
module catalog, manifests, workspace contracts and M16 readiness. It does not
call any LLM provider and it does not fabricate execution status; downstream AI
clients can consume the returned pack as bounded context for explanations.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.ai.prompt_registry import PROMPT_MODULE_EXPLAINER, get_prompt_template
from app.config import Settings, get_settings
from app.core.module_catalog import ModuleCatalogEntry, list_modules, require_module_by_id
from app.core.technique_registry import TechniqueRegistry, create_empty_registry
from app.core.workspace import STANDARD_WORKSPACE_DIRS, workspace_for_module
from app.modules.m16_ops_quality.status import build_m16_readiness_report
from app.modules.registry import manifest_path_for

MODULE_CONTEXT_SCHEMA_VERSION = 1
MODULE_CONTEXT_PURPOSE = "module_context_for_controlled_ai_explanation"
MODULE_CONTEXT_MODE = "metadata_only_no_execution"
MODULE_CONTEXT_PACK_TYPE = "module_catalog_pack"
MODULE_CONTEXT_MAX_TOKENS = 6000
MODULE_CONTEXT_SOURCE_PATHS = (
    "docs/LAIA_CONTEXT_PACKS.md",
    "docs/LAIA_MISTRAL_OPERATING_MODEL.md",
    "docs/MODULE_ACCEPTANCE_CRITERIA.md",
    "app/core/module_catalog.py",
    "app/modules/registry.py",
    "app/core/workspace.py",
    "app/modules/m16_ops_quality/status.py",
)

MODULE_EXPLAINER_RESPONSE_SCHEMA: dict[str, object] = {
    "type": "object",
    "required": [
        "module_id",
        "lifecycle",
        "readiness",
        "execution_implied",
        "user_explanation",
        "next_user_required",
    ],
    "properties": {
        "module_id": {"type": "string"},
        "lifecycle": {"type": "string", "enum": ["official", "reserved"]},
        "readiness": {"type": "string"},
        "execution_implied": {"type": "boolean", "const": False},
        "user_explanation": {"type": "string"},
        "next_user_required": {"type": "boolean"},
    },
}


@dataclass(frozen=True, slots=True)
class ModuleContextItem:
    """JSON-safe context for one product module slot."""

    module: dict[str, Any]
    manifest_path: str
    workspace: dict[str, Any]
    ai_constraints: tuple[str, ...]
    readiness_inputs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable module context item."""
        return {
            "module": dict(self.module),
            "manifest_path": self.manifest_path,
            "workspace": dict(self.workspace),
            "ai_constraints": list(self.ai_constraints),
            "readiness_inputs": dict(self.readiness_inputs),
        }


@dataclass(frozen=True, slots=True)
class ModuleContextPack:
    """Bounded context pack intended for LaIA/Mistral prompts."""

    schema_version: int
    pack_type: str
    purpose: str
    mode: str
    generated_at: str
    max_tokens: int
    source_paths: tuple[str, ...]
    confidence: float
    status: str
    checksum: str
    prompt_id: str
    prompt_template: str
    ai_settings: dict[str, Any]
    m16_readiness: dict[str, Any]
    modules: tuple[ModuleContextItem, ...]

    def to_dict(self, include_checksum: bool = True) -> dict[str, Any]:
        """Return a JSON-serializable context pack."""
        payload = {
            "schema_version": self.schema_version,
            "pack_type": self.pack_type,
            "purpose": self.purpose,
            "mode": self.mode,
            "generated_at": self.generated_at,
            "max_tokens": self.max_tokens,
            "source_paths": list(self.source_paths),
            "confidence": self.confidence,
            "status": self.status,
            "prompt_id": self.prompt_id,
            "prompt_template": self.prompt_template,
            "ai_settings": dict(self.ai_settings),
            "m16_readiness": dict(self.m16_readiness),
            "modules": [item.to_dict() for item in self.modules],
            "module_count": len(self.modules),
        }
        if include_checksum:
            payload["checksum"] = self.checksum
        return payload

    def to_json(self) -> str:
        """Serialize the context pack with stable ordering for logs/tests."""
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


@dataclass(frozen=True, slots=True)
class ModulePromptEnvelope:
    """Prompt-ready envelope for a bounded LaIA/Mistral module explanation."""

    system_instruction: str
    requested_module_id: str
    response_schema: dict[str, object]
    safety_rules: tuple[str, ...]
    context_pack: ModuleContextPack

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable prompt envelope."""
        return {
            "system_instruction": self.system_instruction,
            "requested_module_id": self.requested_module_id,
            "response_schema": dict(self.response_schema),
            "safety_rules": list(self.safety_rules),
            "context_pack": self.context_pack.to_dict(),
            "external_ai_call_performed": False,
        }


def _utc_now_iso() -> str:
    """Return a timezone-aware UTC timestamp for context metadata."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _source_paths_status(source_paths: tuple[str, ...]) -> tuple[float, bool]:
    """Return confidence and existence status for declared source paths."""
    existing = sum(1 for source_path in source_paths if Path(source_path).is_file())
    if not source_paths:
        return 0.0, False
    return existing / len(source_paths), existing == len(source_paths)


def _derive_pack_status(m16_status: str, source_paths_complete: bool) -> str:
    """Derive context-pack readiness using only local source and M16 status."""
    if not source_paths_complete or m16_status == "FAILED":
        return "FAILED"
    if m16_status == "READY_CONTROLLED":
        return "READY"
    return "PARTIAL"


def _payload_checksum(payload: dict[str, Any]) -> str:
    """Return a deterministic checksum for a JSON-safe payload."""
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _build_pack_checksum_payload(
    generated_at: str,
    confidence: float,
    status: str,
    prompt_template: str,
    ai_settings: dict[str, Any],
    m16_readiness: dict[str, Any],
    modules: tuple[ModuleContextItem, ...],
) -> dict[str, Any]:
    """Build the context-pack payload used for checksum calculation."""
    return {
        "schema_version": MODULE_CONTEXT_SCHEMA_VERSION,
        "pack_type": MODULE_CONTEXT_PACK_TYPE,
        "purpose": MODULE_CONTEXT_PURPOSE,
        "mode": MODULE_CONTEXT_MODE,
        "generated_at": generated_at,
        "max_tokens": MODULE_CONTEXT_MAX_TOKENS,
        "source_paths": list(MODULE_CONTEXT_SOURCE_PATHS),
        "confidence": confidence,
        "status": status,
        "prompt_id": PROMPT_MODULE_EXPLAINER,
        "prompt_template": prompt_template,
        "ai_settings": dict(ai_settings),
        "m16_readiness": dict(m16_readiness),
        "modules": [item.to_dict() for item in modules],
        "module_count": len(modules),
    }


def _settings_for_context(settings: Settings | None = None) -> Settings:
    """Return explicit settings or the process settings singleton."""
    return get_settings() if settings is None else settings


def _registry_for_context(registry: TechniqueRegistry | None = None) -> TechniqueRegistry:
    """Return explicit registry or an empty registry when no runtime registry exists."""
    return create_empty_registry() if registry is None else registry


def _techniques_for_module(module: ModuleCatalogEntry, registry: TechniqueRegistry) -> list[dict[str, Any]]:
    """Return real registered technique metadata for a module in stable order."""
    return [
        metadata
        for metadata in registry.to_metadata_list()
        if metadata["module_id"] == module.module_id
    ]


def _workspace_context(module: ModuleCatalogEntry) -> dict[str, Any]:
    """Build workspace metadata without creating directories."""
    workspace = workspace_for_module(module)
    return {
        "root_path": module.workspace_path,
        "manifest_path": f"{module.workspace_path}/workspace_manifest.json",
        "standard_dirs": list(STANDARD_WORKSPACE_DIRS),
        "resolved_root_path": workspace.root_path.as_posix(),
        "execution_implied": False,
    }


def _constraints_for_module(module: ModuleCatalogEntry) -> tuple[str, ...]:
    """Return explicit AI guardrails for one module context item."""
    constraints = [
        "Use catalog and manifest metadata only.",
        "Do not claim tool execution readiness from catalog metadata.",
        "Do not include exploit instructions, payloads or unauthorised actions.",
        "Ask for user-provided module logic when required inputs are absent.",
    ]
    if module.reserved:
        constraints.append("Reserved slots require a user definition before any implementation work.")
    if module.requires_user_definition:
        constraints.append("This module cannot be presented as implemented until the user defines it.")
    return tuple(constraints)


def build_module_context_item(
    module: ModuleCatalogEntry,
    registry: TechniqueRegistry | None = None,
) -> ModuleContextItem:
    """Build deterministic LaIA context for one module catalog entry."""
    selected_registry = _registry_for_context(registry)
    techniques = _techniques_for_module(module, selected_registry)
    module_payload = module.to_dict()
    module_payload["registered_technique_count"] = len(techniques)
    module_payload["registered_techniques"] = techniques
    return ModuleContextItem(
        module=module_payload,
        manifest_path=manifest_path_for(module).as_posix(),
        workspace=_workspace_context(module),
        ai_constraints=_constraints_for_module(module),
        readiness_inputs={
            "catalog_readiness": module.readiness,
            "requires_user_definition": module.requires_user_definition,
            "registered_technique_count": len(techniques),
            "execution_readiness_sources": ["ToolHealth", "VersionLock", "PolicyEngine", "target_scope", "worker_state"],
            "external_ai_call_performed": False,
        },
    )


def build_module_context_pack(
    include_reserved: bool = True,
    settings: Settings | None = None,
    registry: TechniqueRegistry | None = None,
) -> ModuleContextPack:
    """Build the complete module context pack without contacting external services."""
    selected_settings = _settings_for_context(settings)
    selected_registry = _registry_for_context(registry)
    modules = tuple(
        build_module_context_item(module, registry=selected_registry)
        for module in list_modules(include_reserved=include_reserved)
    )
    readiness = build_m16_readiness_report(env={
        "AI_ENABLED": "1" if selected_settings.ai_enabled else "0",
        "MISTRAL_ENABLED": "1" if selected_settings.mistral_enabled else "0",
        "ANGEL_ENABLED": "1" if selected_settings.angel_enabled else "0",
        "MISTRAL_MODEL": selected_settings.mistral_model,
        "DEEPSEEK_API_KEY": selected_settings.deepseek_api_key,
    })
    generated_at = _utc_now_iso()
    prompt_template = get_prompt_template(PROMPT_MODULE_EXPLAINER)
    ai_settings = selected_settings.sanitized_ai_settings()
    m16_readiness = {
        "module_id": readiness.module_id,
        "status": readiness.status,
        "generated_at": readiness.generated_at,
        "component_count": len(readiness.components),
    }
    source_confidence, source_paths_complete = _source_paths_status(MODULE_CONTEXT_SOURCE_PATHS)
    status = _derive_pack_status(readiness.status, source_paths_complete)
    checksum_payload = _build_pack_checksum_payload(
        generated_at=generated_at,
        confidence=source_confidence,
        status=status,
        prompt_template=prompt_template,
        ai_settings=ai_settings,
        m16_readiness=m16_readiness,
        modules=modules,
    )
    return ModuleContextPack(
        schema_version=MODULE_CONTEXT_SCHEMA_VERSION,
        pack_type=MODULE_CONTEXT_PACK_TYPE,
        purpose=MODULE_CONTEXT_PURPOSE,
        mode=MODULE_CONTEXT_MODE,
        generated_at=generated_at,
        max_tokens=MODULE_CONTEXT_MAX_TOKENS,
        source_paths=MODULE_CONTEXT_SOURCE_PATHS,
        confidence=source_confidence,
        status=status,
        checksum=_payload_checksum(checksum_payload),
        prompt_id=PROMPT_MODULE_EXPLAINER,
        prompt_template=prompt_template,
        ai_settings=ai_settings,
        m16_readiness=m16_readiness,
        modules=modules,
    )


def explain_module_for_ai(
    module_id: str,
    settings: Settings | None = None,
    registry: TechniqueRegistry | None = None,
) -> dict[str, Any]:
    """Return a bounded explanation payload for one module without running an LLM."""
    module = require_module_by_id(module_id)
    selected_registry = _registry_for_context(registry)
    context_item = build_module_context_item(module, registry=selected_registry)
    pack = build_module_context_pack(include_reserved=True, settings=settings, registry=selected_registry)
    return {
        "schema_version": MODULE_CONTEXT_SCHEMA_VERSION,
        "module_id": module.module_id,
        "display_name": module.display_name,
        "lifecycle": module.lifecycle,
        "readiness": module.readiness,
        "workspace_path": module.workspace_path,
        "manifest_path": module.manifest_path,
        "requires_user_definition": module.requires_user_definition,
        "execution_implied": False,
        "ai_backend": pack.ai_settings["ai_backend"],
        "mistral_model": pack.ai_settings["mistral_model"],
        "m16_status": pack.m16_readiness["status"],
        "context": context_item.to_dict(),
        "explanation": (
            f"{module.display_name} is a {module.lifecycle} Ojo de Dios module slot. "
            "This response is deterministic metadata for LaIA/Mistral context and does not execute tools."
        ),
        "next_user_required": module.requires_user_definition,
    }


def build_module_prompt_envelope(
    module_id: str,
    settings: Settings | None = None,
    registry: TechniqueRegistry | None = None,
) -> ModulePromptEnvelope:
    """Build a prompt-ready envelope for LaIA/Mistral without calling the model."""
    module = require_module_by_id(module_id)
    selected_registry = _registry_for_context(registry)
    pack = build_module_context_pack(include_reserved=True, settings=settings, registry=selected_registry)
    return ModulePromptEnvelope(
        system_instruction=(
            "You are LaIA for Ojo de Dios. Explain only the requested module using the provided "
            "JSON context. Do not invent techniques, readiness, target data or execution results. "
            "Return JSON matching response_schema."
        ),
        requested_module_id=module.module_id,
        response_schema=MODULE_EXPLAINER_RESPONSE_SCHEMA,
        safety_rules=(
            "Use only context_pack data.",
            "Do not execute tools or imply that tools were executed.",
            "Do not provide exploit payloads, bypass instructions or unauthorised actions.",
            "For reserved modules, state that user definition is required before implementation.",
        ),
        context_pack=pack,
    )

# Target-bound artifact context is deliberately separate from the catalog context above.
# Catalog context explains the product; these helpers expose only real saved files for one target module.
TARGET_MODULE_CONTEXT_MAX_FILES = 24
TARGET_MODULE_CONTEXT_MAX_FILE_CHARS = 4_000
TARGET_MODULE_CONTEXT_MAX_CHARS = 32_000
_TARGET_MODULE_CONTEXT_SUFFIXES = {".json", ".md", ".txt", ".csv", ".log"}
_TARGET_MODULE_CONTEXT_EXCLUDED_DIRS = frozenset({"ai_reviews", "tmp"})
_TARGET_MODULE_FINDING_DIRS = frozenset({"evidence", "outputs"})


def _require_target_context_module(module_id: str) -> ModuleCatalogEntry:
    module = require_module_by_id(module_id)
    if module.module_number == 1:
        raise ValueError("M01 has a dedicated evidence and LaIA context flow.")
    if not module.official:
        raise ValueError("Target module AI context is available only for official modules M02 through M16.")
    return module


def _json_object_from_path(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _derive_target_module_context_findings(module_id: str, workspace_root: Path) -> tuple[dict[str, Any], ...]:
    """Derive finding context from persisted module evidence and outputs only."""
    from app.core.module_findings import derive_target_module_findings

    findings_by_id: dict[str, dict[str, Any]] = {}
    for directory_name in sorted(_TARGET_MODULE_FINDING_DIRS):
        directory = workspace_root / directory_name
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.json")):
            payload = _json_object_from_path(path)
            if payload is None:
                continue
            for finding in derive_target_module_findings(module_id, payload):
                item = finding.to_dict()
                refs = item.get("evidence_refs", [])
                if not isinstance(refs, list):
                    refs = []
                artifact_ref = path.relative_to(workspace_root).as_posix()
                if artifact_ref not in refs:
                    refs.append(artifact_ref)
                item["evidence_refs"] = refs
                findings_by_id[str(item["finding_id"])] = item
    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    return tuple(
        sorted(
            findings_by_id.values(),
            key=lambda item: (
                severity_order.get(str(item.get("severity") or "").casefold(), 9),
                str(item.get("title") or ""),
                str(item.get("finding_id") or ""),
            ),
        )
    )


def _previous_review_context(target: "TargetRecord", module_id: str, repo_root: Path, limit: int = 3) -> tuple[dict[str, Any], ...]:
    """Return bounded previous local-review context without raw review bodies."""
    reviews: list[dict[str, Any]] = []
    for review in list_target_module_ai_reviews(target, module_id, repo_root=repo_root, limit=limit):
        reviews.append({
            "review_id": review.get("review_id"),
            "model": review.get("model"),
            "created_at": review.get("created_at"),
            "path": review.get("path"),
            "parse_status": review.get("parse_status"),
            "parsed_content": review.get("parsed_content"),
        })
    return tuple(reviews)


def build_target_module_context_pack(
    target: "TargetRecord",
    module_id: str,
    repo_root: Path | None = None,
    extra_findings: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    source_stored_evidence_count: int = 0,
    unverified_stored_evidence_count: int = 0,
) -> dict[str, Any]:
    """Build bounded LaIA input from actual artifacts saved in one target-module workspace."""
    from app.core.module_action_plan import build_module_action_plan
    from app.core.target_workspace import bind_target_module_workspace

    module = _require_target_context_module(module_id)
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, module_id, repo_root=root)
    remaining = TARGET_MODULE_CONTEXT_MAX_CHARS
    artifacts: list[dict[str, Any]] = []
    all_files = [path for path in binding.root_path.rglob("*") if path.is_file() and path != binding.manifest_path]
    files = sorted(
        (
            path
            for path in all_files
            if not any(part in _TARGET_MODULE_CONTEXT_EXCLUDED_DIRS for part in path.relative_to(binding.root_path).parts)
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    workspace_findings = _derive_target_module_context_findings(module.module_id, binding.root_path)
    findings_by_id = {str(item.get("finding_id")): item for item in workspace_findings}
    stored_evidence_finding_count = 0
    for finding in extra_findings or ():
        if not isinstance(finding, dict):
            continue
        finding_id = str(finding.get("finding_id") or "")
        if not finding_id:
            continue
        findings_by_id.setdefault(finding_id, dict(finding))
        stored_evidence_finding_count += 1
    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings = tuple(
        sorted(
            findings_by_id.values(),
            key=lambda item: (
                severity_order.get(str(item.get("severity") or "").casefold(), 9),
                str(item.get("title") or ""),
                str(item.get("finding_id") or ""),
            ),
        )
    )
    action_plan = build_module_action_plan(
        target,
        module.module_id,
        findings=list(findings),
        repo_root=root,
        source_stored_evidence_count=source_stored_evidence_count,
        unverified_stored_evidence_count=unverified_stored_evidence_count,
    ).to_dict()
    previous_reviews = _previous_review_context(target, module.module_id, root)
    for path in files[:TARGET_MODULE_CONTEXT_MAX_FILES]:
        item: dict[str, Any] = {
            "path": path.relative_to(binding.root_path).as_posix(),
            "size_bytes": path.stat().st_size,
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat(),
        }
        if path.suffix.lower() in _TARGET_MODULE_CONTEXT_SUFFIXES and remaining > 0:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                content = ""
            excerpt = content[: min(TARGET_MODULE_CONTEXT_MAX_FILE_CHARS, remaining)]
            if excerpt:
                item["excerpt"] = excerpt
                item["truncated"] = len(excerpt) < len(content)
                remaining -= len(excerpt)
        artifacts.append(item)
    return {
        "pack_type": "target_module_local_context_pack",
        "target_id": target.target_id,
        "module_id": module.module_id,
        "module_number": module.module_number,
        "generated_at": datetime.now(UTC).isoformat(),
        "workspace_path": binding.root_path.as_posix(),
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "findings": list(findings),
        "finding_count": len(findings),
        "workspace_finding_count": len(workspace_findings),
        "stored_evidence_finding_count": stored_evidence_finding_count,
        "source_stored_evidence_count": max(int(source_stored_evidence_count), 0),
        "unverified_stored_evidence_count": max(int(unverified_stored_evidence_count), 0),
        "action_plan": action_plan,
        "previous_reviews": list(previous_reviews),
        "previous_review_count": len(previous_reviews),
        "excluded_artifact_count": len(all_files) - len(files),
        "excluded_directories": sorted(_TARGET_MODULE_CONTEXT_EXCLUDED_DIRS),
        "safety": {
            "uses_target_module_workspace_only": True,
            "external_ai_call_performed": False,
            "local_ai_call_performed": False,
            "target_activity_performed": False,
            "unverified_stored_evidence_excluded": max(int(unverified_stored_evidence_count), 0),
        },
    }


def render_target_module_chatml_prompt(
    target: "TargetRecord",
    module_id: str,
    repo_root: Path | None = None,
    extra_findings: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    source_stored_evidence_count: int = 0,
    unverified_stored_evidence_count: int = 0,
) -> dict[str, Any]:
    """Render a no-call local ChatML review prompt for saved target-module artifacts."""
    pack = build_target_module_context_pack(
        target,
        module_id,
        repo_root=repo_root,
        extra_findings=extra_findings,
        source_stored_evidence_count=source_stored_evidence_count,
        unverified_stored_evidence_count=unverified_stored_evidence_count,
    )
    instruction = (
        "Eres LaIA/Mistral local de Ojo de Dios. Analiza solo los artefactos incluidos. "
        "No inventes evidencia ni ejecutes técnicas. Devuelve JSON con summary, confirmed_findings, "
        "recommended_next_steps, missing_evidence y safety_notes."
    )
    envelope = {"mode": "target_module_laia_local_review", "system": instruction, "context_pack": pack}
    prompt = f"<|system|>\n{instruction}\n<|user|>\n{json.dumps(envelope, ensure_ascii=False, indent=2)}\n<|assistant|>\n"
    return {
        "target_id": target.target_id,
        "module_id": module_id,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "external_ai_call_performed": False,
        "local_ai_call_performed": False,
    }


def _extract_first_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
    """Extract the first JSON object from raw local review text."""
    stripped = text.strip()
    candidates = [stripped]
    candidates.extend(
        match.group(1).strip()
        for match in re.finditer(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    )
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidates.append(text[first_brace : last_brace + 1])
    last_error = "No JSON object found in local review content."
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            continue
        if isinstance(payload, dict):
            return payload, None
    return None, last_error


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_target_module_review_payload(payload: dict[str, object]) -> dict[str, object]:
    """Normalize a local module review into a stable operator-facing schema."""
    return {
        "summary": str(payload.get("summary", "")).strip(),
        "confirmed_findings": _string_list(payload.get("confirmed_findings", [])),
        "recommended_next_steps": _string_list(payload.get("recommended_next_steps", [])),
        "missing_evidence": _string_list(payload.get("missing_evidence", [])),
        "safety_notes": _string_list(payload.get("safety_notes", [])),
    }


def _review_from_payload(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    content = str(payload.get("content", ""))
    maybe_json, parse_error = _extract_first_json_object(content)
    parsed_content = normalize_target_module_review_payload(maybe_json) if maybe_json is not None else None
    review = dict(payload)
    review["path"] = path.as_posix()
    review["parsed_content"] = parsed_content
    review["parse_status"] = "parsed" if parsed_content is not None else "raw_text"
    review["parse_error"] = parse_error
    return review


def write_target_module_ai_review(
    target: "TargetRecord", module_id: str, model: str, prompt_sha256: str, content: str, repo_root: Path | None = None
) -> Path:
    """Persist an explicitly generated local review receipt within the target module workspace."""
    from app.core.target_workspace import bind_target_module_workspace

    _require_target_context_module(module_id)
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, module_id, repo_root=root)
    reviews_dir = binding.root_path / "ai_reviews" / "laia_mistral"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(UTC).isoformat()
    review_id = hashlib.sha256(f"{target.target_id}:{module_id}:{model}:{prompt_sha256}:{created_at}".encode("utf-8")).hexdigest()[:16]
    path = reviews_dir / f"{review_id}.json"
    path.write_text(json.dumps({
        "review_id": review_id, "target_id": target.target_id, "module_id": module_id,
        "model": model, "prompt_sha256": prompt_sha256, "content": content, "created_at": created_at,
        "external_ai_call_performed": False, "local_ai_call_performed": True, "target_activity_performed": False,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def list_target_module_ai_reviews(
    target: "TargetRecord", module_id: str, repo_root: Path | None = None, limit: int = 20
) -> tuple[dict[str, Any], ...]:
    """List valid local LaIA review receipts stored for one official target module."""
    from app.core.target_workspace import bind_target_module_workspace

    _require_target_context_module(module_id)
    if limit < 1:
        raise ValueError("Review limit must be at least 1.")
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, module_id, repo_root=root)
    reviews_dir = binding.root_path / "ai_reviews" / "laia_mistral"
    if not reviews_dir.is_dir():
        return ()
    reviews: list[dict[str, Any]] = []
    for path in sorted(reviews_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        if payload.get("target_id") != target.target_id or payload.get("module_id") != module_id:
            continue
        reviews.append(_review_from_payload(path, payload))
        if len(reviews) >= limit:
            break
    return tuple(reviews)
