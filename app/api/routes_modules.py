"""Module catalog and M16 readiness API routes."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.ai.hermes_assist import (
    HermesAssistRequest,
    HermesDeepSeekAssistService,
    build_hermes_deepseek_chat_request,
)
from app.ai.hermes_receipts import (
    build_hermes_receipt_context_pack,
    build_laia_receipt_review_context_pack,
    build_hermes_receipt_prompt_envelope,
    build_laia_receipt_review_prompt_envelope,
    list_hermes_assist_receipts,
    list_laia_receipt_reviews,
    read_hermes_assist_receipt,
    read_laia_receipt_review,
    redact_hermes_payload,
    render_laia_receipt_review_chatml_prompt,
    summarize_laia_receipt_reviews,
    render_hermes_receipt_chatml_prompt,
    summarize_hermes_assist_receipts,
    write_hermes_assist_receipt,
    write_laia_receipt_review,
    write_laia_review_receipt_audit,
)
from app.ai.mistral_client import MistralClient
from app.ai.module_context import build_module_context_pack, build_module_prompt_envelope, explain_module_for_ai
from app.ai.tool_install_context import build_tool_install_context_pack
from app.ai.tool_run_context import build_tool_run_context_pack
from app.config import get_settings
from app.core.errors import ConfigurationError, ContractError
from app.core.m01_findings import derive_m01_passive_findings
from app.core.osint_domain_snapshot import build_passive_domain_snapshot, write_domain_snapshot
from app.core.module_catalog import get_module_by_id, list_modules, module_catalog_as_dicts
from app.core.knowledge_base import (
    build_knowledge_base,
    build_knowledge_context_pack,
    read_knowledge_status,
    search_knowledge_base,
)
from app.core.runtime_registry import get_runtime_registry_snapshot
from app.core.tool_definition import list_tool_definitions_for_module
from app.core.tool_install_plan import build_module_tool_install_plan
from app.core.tool_install_receipts import list_tool_install_receipts, read_tool_install_receipt
from app.core.tool_install_workspace import prepare_module_tool_install_plan, read_prepared_module_tool_install_plan
from app.core.tool_inventory import list_documented_tools_for_module
from app.core.tool_registry import load_module_tool_registry
from app.core.tool_run_lifecycle import update_tool_run_status
from app.core.tool_run_summary import summarize_tool_run_workspace
from app.core.technique_catalog import list_module_techniques, summarize_module_techniques
from app.core.technique_workspace import (
    ensure_all_technique_workspaces,
    ensure_module_technique_workspaces,
    ensure_technique_workspace,
    inspect_technique_workspace,
    list_technique_workspace_artifacts,
    read_technique_workspace_json_artifact,
    write_technique_workspace_json_artifact,
)
from app.core.version_lock import VersionLockEntry, create_needs_review_lock_from_tool_definition
from app.core.windows_first_run import build_first_run_report, write_first_run_status
from app.core.windows_station_manifest import build_windows_station_manifest
from app.core.workspace_artifacts import (
    list_tool_run_artifacts,
    read_tool_run_json_artifact,
    write_tool_run_input_artifact,
    write_tool_run_json_artifact,
)
from app.core.workspace import start_tool_run_workspace
from app.core.workspace_bootstrap import bootstrap_module_workspace
from app.core.workspace_state import collect_module_workspace_state
from app.db.models import VersionLock
from app.db.repositories.version_lock_repository import VersionLockRepository
from app.db.session import get_session
from app.modules.m16_ops_quality.status import build_m16_readiness_report, check_python_tool_health, read_m16_readiness_history, run_m16_operational_action, write_runtime_status
from app.modules.m18_honeypots_deception.techniques import build_ioc_event_timeline
from app.modules.registry import ModuleManifestError, load_module_manifest

router = APIRouter()


def _settings_to_m16_env() -> dict[str, str]:
    """Convert settings into the uppercase flags consumed by M16 readiness checks."""
    settings = get_settings()
    return {
        "AI_ENABLED": "1" if settings.ai_enabled else "0",
        "MISTRAL_ENABLED": "1" if settings.mistral_enabled else "0",
        "ANGEL_ENABLED": "1" if settings.angel_enabled else "0",
        "MISTRAL_MODEL": settings.mistral_model,
        "DEEPSEEK_API_KEY": settings.deepseek_api_key,
    }


def _version_lock_entry_to_payload(entry: VersionLockEntry) -> dict[str, Any]:
    return {
        "tool_id": entry.tool_id,
        "tool_name": entry.tool_name,
        "module_id": entry.module_id,
        "recommended_version": entry.recommended_version,
        "resolved_version": entry.resolved_version,
        "source_url": entry.source_url,
        "runtime": entry.runtime,
        "binary_hash": entry.binary_hash,
        "locked_at": entry.locked_at,
        "status": entry.status,
    }


def _version_lock_to_payload(lock: VersionLock) -> dict[str, Any]:
    return {
        "tool_id": lock.tool_id,
        "tool_name": lock.tool_name,
        "module_id": lock.module_id,
        "recommended_version": lock.recommended_version,
        "resolved_version": lock.resolved_version,
        "source_url": lock.source_url,
        "runtime": lock.runtime,
        "binary_hash": lock.binary_hash,
        "locked_at": lock.locked_at.isoformat() if lock.locked_at else None,
        "status": lock.status,
    }


def get_local_mistral_client() -> MistralClient:
    """Build the configured local Mistral client for dependency overrides."""
    settings = get_settings()
    return MistralClient(
        base_url=settings.ollama_base_url,
        model=settings.mistral_model,
        timeout_seconds=settings.mistral_timeout_seconds,
        enabled=settings.ai_enabled and settings.mistral_enabled,
    )


def get_hermes_assist_service() -> HermesDeepSeekAssistService:
    """Build the configured Hermes/DeepSeek assist service for dependency overrides."""
    return HermesDeepSeekAssistService(get_settings())


def _hermes_assist_request_from_payload(payload: dict[str, Any], settings_model: str) -> HermesAssistRequest:
    context = payload.get("context", {})
    if not isinstance(context, dict):
        raise HTTPException(status_code=400, detail="Hermes context must be a JSON object.")
    try:
        max_tokens = int(payload.get("max_tokens", 1200))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Hermes max_tokens must be an integer.") from exc
    return HermesAssistRequest(
        question=str(payload.get("question", "")),
        context=context,
        purpose=str(payload.get("purpose", "tooling_or_code_research")),
        model=str(payload.get("model", settings_model)),
        allow_pro_model=bool(payload.get("allow_pro_model", False)),
        max_tokens=max_tokens,
        reasoning_effort=str(payload.get("reasoning_effort", "low")),
    )


def _knowledge_augmented_hermes_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a Hermes payload with optional local knowledge context injected."""
    if payload.get("use_knowledge_base") is not True:
        return dict(payload)
    context = payload.get("context", {})
    if not isinstance(context, dict):
        raise HTTPException(status_code=400, detail="Hermes context must be a JSON object.")
    try:
        limit = int(payload.get("knowledge_limit", 5))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Hermes knowledge_limit must be an integer.") from exc
    query = str(payload.get("knowledge_query") or payload.get("question", ""))
    try:
        knowledge_context = build_knowledge_context_pack(query=query, limit=limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=409, detail="Knowledge base must be built before use_knowledge_base=true.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    augmented = dict(payload)
    augmented["context"] = {
        **context,
        "local_knowledge_context": knowledge_context,
    }
    return augmented


@router.get("/api/modules")
def list_module_catalog(include_reserved: bool = True) -> dict[str, Any]:
    """Return product module catalog entries in stable module order."""
    modules = module_catalog_as_dicts(include_reserved=include_reserved)
    return {
        "modules": modules,
        "count": len(modules),
        "include_reserved": include_reserved,
    }


@router.get("/api/runtime/registry")
def get_runtime_registry_status() -> dict[str, Any]:
    """Return concrete runtime technique registry status without executing techniques."""
    snapshot = get_runtime_registry_snapshot()
    return snapshot.to_status_payload()


@router.get("/api/modules/{module_id}")
def get_module(module_id: str) -> dict[str, Any]:
    """Return one module catalog entry by stable module id."""
    module = get_module_by_id(module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"module": module.to_dict()}


@router.get("/api/modules/techniques/summary")
def get_modules_techniques_summary(include_reserved: bool = False) -> dict[str, Any]:
    """Return documentation-backed technique counts by module without executing techniques."""
    return {"summary": summarize_module_techniques(include_reserved=include_reserved)}


@router.get("/api/modules/m18_honeypots_deception/ioc-timeline")
def get_m18_ioc_timeline(limit: int = 100) -> dict[str, Any]:
    """Return the persisted M18 IOC event timeline for dashboard visualization."""
    db_path = Path("storage/workspaces/m18_honeypots_deception/ioc_history.sqlite3")
    return {"timeline": build_ioc_event_timeline(db_path, limit=limit)}


@router.get("/api/modules/{module_id}/techniques")
def get_module_techniques(module_id: str) -> dict[str, Any]:
    """Return documentation-backed technique entries for one module without executing techniques."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    techniques = [technique.to_dict() for technique in list_module_techniques(module_id)]
    return {
        "module_id": module_id,
        "techniques": techniques,
        "count": len(techniques),
        "execution_implied": False,
    }


@router.get("/api/modules/{module_id}/techniques/{technique_id}/workspace")
def get_module_technique_workspace_api(module_id: str, technique_id: str) -> dict[str, Any]:
    """Inspect a technique workspace without creating or executing it."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        return inspect_technique_workspace(module_id, technique_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Technique not found.") from exc


@router.post("/api/modules/{module_id}/techniques/{technique_id}/workspace/bootstrap")
def bootstrap_module_technique_workspace_api(module_id: str, technique_id: str) -> dict[str, Any]:
    """Create a technique workspace manifest without executing the technique."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        workspace = ensure_technique_workspace(module_id, technique_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Technique not found.") from exc
    return {
        "workspace": workspace.to_dict(),
        "execution_implied": False,
    }


@router.post("/api/modules/{module_id}/techniques/workspaces/bootstrap")
def bootstrap_module_technique_workspaces_api(module_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Create workspaces for all documented techniques in one module without execution."""
    if payload.get("execute_bootstrap") is not True:
        raise HTTPException(status_code=400, detail="Technique workspace bootstrap requires execute_bootstrap=true.")
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    workspaces = ensure_module_technique_workspaces(module_id)
    return {
        "module_id": module_id,
        "workspace_count": len(workspaces),
        "workspaces": [workspace.to_dict() for workspace in workspaces],
        "execution_implied": False,
    }


@router.post("/api/ops/technique-workspaces/bootstrap")
def bootstrap_all_technique_workspaces_api(payload: dict[str, Any]) -> dict[str, Any]:
    """Create workspaces for all documented techniques in catalog order without execution."""
    if payload.get("execute_bootstrap") is not True:
        raise HTTPException(status_code=400, detail="Technique workspace bootstrap requires execute_bootstrap=true.")
    include_reserved = bool(payload.get("include_reserved", False))
    summary = ensure_all_technique_workspaces(include_reserved=include_reserved)
    return {
        "mode": "all_documented_technique_workspace_bootstrap",
        "summary": summary,
        "execution_implied": False,
    }


@router.get("/api/modules/{module_id}/techniques/{technique_id}/workspace/artifacts")
def list_module_technique_workspace_artifacts_api(module_id: str, technique_id: str) -> dict[str, Any]:
    """List JSON artifacts in a technique workspace without executing the technique."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        artifacts = [artifact.to_dict() for artifact in list_technique_workspace_artifacts(module_id, technique_id)]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Technique not found.") from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Technique workspace not found.") from exc
    return {"module_id": module_id, "technique_id": technique_id, "artifacts": artifacts, "count": len(artifacts)}


@router.post("/api/modules/{module_id}/techniques/{technique_id}/workspace/artifacts")
def write_module_technique_workspace_artifact_api(
    module_id: str, technique_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """Write one JSON artifact into a technique workspace without executing the technique."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    artifact_payload = payload.get("payload", {})
    if not isinstance(artifact_payload, dict):
        raise HTTPException(status_code=400, detail="Technique artifact payload must be a JSON object.")
    try:
        artifact = write_technique_workspace_json_artifact(
            module_id=module_id,
            technique_id=technique_id,
            artifact_name=str(payload.get("artifact_name", "artifact")),
            artifact_type=str(payload.get("artifact_type", "input")),
            payload=artifact_payload,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Technique not found.") from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Technique workspace not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"artifact": artifact.to_dict(), "execution_implied": False}


@router.get("/api/modules/{module_id}/techniques/{technique_id}/workspace/artifacts/{artifact_name}")
def read_module_technique_workspace_artifact_api(
    module_id: str, technique_id: str, artifact_name: str, artifact_type: str = "input"
) -> dict[str, Any]:
    """Read one JSON artifact from a technique workspace without executing the technique."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        artifact, artifact_payload = read_technique_workspace_json_artifact(
            module_id, technique_id, artifact_name, artifact_type
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Technique not found.") from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Technique artifact not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"artifact": artifact.to_dict(), "payload": artifact_payload, "execution_implied": False}


@router.get("/api/modules/{module_id}/manifest")
def get_module_manifest(module_id: str) -> dict[str, Any]:
    """Return one physical module manifest after validating its catalog identity."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        manifest = load_module_manifest(module_id)
    except ModuleManifestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"manifest": manifest}


@router.get("/api/modules/{module_id}/documented-tools")
def get_module_documented_tools(module_id: str) -> dict[str, Any]:
    """Return documentation-backed tool inventory for one module without executing tools."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    tools = [item.to_dict() for item in list_documented_tools_for_module(module_id)]
    return {"module_id": module_id, "tools": tools, "count": len(tools), "execution_implied": False}


@router.get("/api/modules/{module_id}/tool-definitions")
def get_module_tool_definitions(module_id: str) -> dict[str, Any]:
    """Return validated tool definitions for one module without executing tools."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    definitions = [definition.to_dict() for definition in list_tool_definitions_for_module(module_id)]
    return {"module_id": module_id, "tool_definitions": definitions, "count": len(definitions), "execution_implied": False}


@router.get("/api/modules/{module_id}/tool-registry")
def get_module_tool_registry(module_id: str) -> dict[str, Any]:
    """Return module-scoped ToolRegistry metadata without executing tools."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    registry = load_module_tool_registry(module_id)
    return {
        "module_id": module_id,
        "registry_keys": registry.list_keys(),
        "tool_definitions": registry.to_metadata_list(),
        "count": registry.count(),
        "execution_implied": False,
    }


@router.get("/api/modules/{module_id}/install-plan")
def get_module_tool_install_plan(module_id: str) -> dict[str, Any]:
    """Return a reviewable, non-executing install plan for module tools."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"install_plan": build_module_tool_install_plan(module_id).to_dict()}


@router.post("/api/modules/{module_id}/install-plan/prepare")
def prepare_module_tool_install_plan_api(module_id: str) -> dict[str, Any]:
    """Persist the current non-executing install plan into the module workspace."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    persisted = prepare_module_tool_install_plan(module_id)
    return {"prepared_install_plan": persisted.to_dict()}


@router.get("/api/modules/{module_id}/install-plan/prepared")
def get_prepared_module_tool_install_plan_api(module_id: str) -> dict[str, Any]:
    """Read a previously persisted non-executing install plan from the workspace."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        persisted, payload = read_prepared_module_tool_install_plan(module_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Prepared install plan not found.") from exc
    return {"prepared_install_plan": persisted.to_dict(), "payload": payload}


@router.get("/api/modules/{module_id}/install-receipts")
def list_module_tool_install_receipts_api(module_id: str) -> dict[str, Any]:
    """List persisted guarded install receipts for a module."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    receipts = [receipt.to_dict() for receipt in list_tool_install_receipts(module_id)]
    return {"module_id": module_id, "install_receipts": receipts, "count": len(receipts)}


@router.get("/api/modules/{module_id}/install-receipts/{receipt_id}")
def get_module_tool_install_receipt_api(module_id: str, receipt_id: str) -> dict[str, Any]:
    """Read one persisted guarded install receipt for a module."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        receipt = read_tool_install_receipt(module_id, receipt_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Install receipt not found.") from exc
    return {"install_receipt": receipt.to_dict()}


@router.get("/api/modules/{module_id}/version-locks/candidates")
def get_module_version_lock_candidates(module_id: str) -> dict[str, Any]:
    """Return needs-review VersionLock candidates derived from registered tools."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    registry = load_module_tool_registry(module_id)
    candidates = [
        _version_lock_entry_to_payload(create_needs_review_lock_from_tool_definition(definition, module_id))
        for definition in registry.list_all()
    ]
    return {"module_id": module_id, "version_lock_candidates": candidates, "count": len(candidates), "persisted": False}


@router.post("/api/modules/{module_id}/version-locks/bootstrap")
def bootstrap_module_version_locks(
    module_id: str,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Persist needs-review VersionLock entries for a module's registered tools."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    registry = load_module_tool_registry(module_id)
    repository = VersionLockRepository(session)
    persisted = []
    for definition in registry.list_all():
        entry = create_needs_review_lock_from_tool_definition(definition, module_id)
        persisted.append(repository.upsert_lock(entry))
    session.commit()
    return {
        "module_id": module_id,
        "version_locks": [_version_lock_to_payload(lock) for lock in persisted],
        "count": len(persisted),
        "persisted": True,
    }


@router.get("/api/modules/{module_id}/workspace/state")
def get_module_workspace_state(module_id: str) -> dict[str, Any]:
    """Return current module/tool/run workspace state without creating files."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"workspace_state": collect_module_workspace_state(module_id).to_dict()}


@router.post("/api/modules/{module_id}/workspace/bootstrap")
def bootstrap_module_workspace_api(
    module_id: str,
    include_documented_tools: bool = True,
) -> dict[str, Any]:
    """Create module and documented-tool workspaces for one module."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    result = bootstrap_module_workspace(module_id, include_documented_tools=include_documented_tools)
    return {"bootstrap": result.to_dict()}


@router.post("/api/modules/{module_id}/tool-runs")
def start_module_tool_run_api(
    module_id: str,
    tool_id: str,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Prepare a per-run workspace for a module tool without executing it."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    run_workspace = start_tool_run_workspace(module_id, tool_id, run_id=run_id)
    return {"tool_run_workspace": run_workspace.to_dict()}


@router.patch("/api/modules/{module_id}/tool-runs/{run_id}/status")
def update_module_tool_run_status_api(
    module_id: str,
    run_id: str,
    tool_id: str,
    status: str,
    note: str | None = None,
) -> dict[str, Any]:
    """Persist a lifecycle status update for an existing prepared tool run."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    if status not in {"prepared", "running", "completed", "failed", "cancelled"}:
        raise HTTPException(status_code=400, detail="Unsupported tool-run status.")
    try:
        update = update_tool_run_status(module_id, tool_id, run_id, status, note=note)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Tool run not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"tool_run_lifecycle": update.to_dict()}


@router.get("/api/modules/{module_id}/tool-runs/{run_id}")
def get_module_tool_run_summary_api(
    module_id: str,
    run_id: str,
    tool_id: str,
) -> dict[str, Any]:
    """Return manifest and artifact summary for one prepared tool-run workspace."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        summary = summarize_tool_run_workspace(module_id, tool_id, run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Tool run not found.") from exc
    return {"tool_run_summary": summary.to_dict()}


@router.post("/api/modules/{module_id}/tool-runs/{run_id}/inputs")
def write_module_tool_run_input_api(
    module_id: str,
    run_id: str,
    tool_id: str,
    artifact_name: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Write a JSON input artifact into a prepared tool-run workspace."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    artifact = write_tool_run_input_artifact(module_id, tool_id, run_id, artifact_name, payload)
    return {"artifact": artifact.to_dict()}


@router.post("/api/modules/{module_id}/tool-runs/{run_id}/artifacts")
def write_module_tool_run_artifact_api(
    module_id: str,
    run_id: str,
    tool_id: str,
    artifact_name: str,
    artifact_type: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Write a JSON artifact into a prepared tool-run workspace."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    if artifact_type not in {"input", "output", "evidence", "log"}:
        raise HTTPException(status_code=400, detail="Unsupported artifact type.")
    artifact = write_tool_run_json_artifact(module_id, tool_id, run_id, artifact_name, payload, artifact_type)
    return {"artifact": artifact.to_dict()}


@router.get("/api/modules/{module_id}/tool-runs/{run_id}/artifacts")
def list_module_tool_run_artifacts_api(
    module_id: str,
    run_id: str,
    tool_id: str,
) -> dict[str, Any]:
    """List JSON artifacts currently stored in a prepared tool-run workspace."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    artifacts = [artifact.to_dict() for artifact in list_tool_run_artifacts(module_id, tool_id, run_id)]
    return {"artifacts": artifacts, "count": len(artifacts)}


@router.get("/api/modules/{module_id}/tool-runs/{run_id}/artifacts/{artifact_name}")
def read_module_tool_run_artifact_api(
    module_id: str,
    run_id: str,
    artifact_name: str,
    tool_id: str,
    artifact_type: str,
) -> dict[str, Any]:
    """Read one JSON artifact payload and metadata from a prepared tool-run workspace."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    if artifact_type not in {"input", "output", "evidence", "log"}:
        raise HTTPException(status_code=400, detail="Unsupported artifact type.")
    try:
        artifact, payload = read_tool_run_json_artifact(module_id, tool_id, run_id, artifact_name, artifact_type)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Artifact not found.") from exc
    return {"artifact": artifact.to_dict(), "payload": payload}


@router.post("/api/modules/m01_osint/osint/domain-snapshot")
def create_m01_passive_domain_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a passive DNS-only OSINT snapshot for M01 and persist it in the workspace."""
    domain = str(payload.get("domain", ""))
    persist = payload.get("persist", True) is not False
    include_external = payload.get("include_external", False) is True
    try:
        snapshot = build_passive_domain_snapshot(domain, include_external=include_external)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    artifact_path = write_domain_snapshot(snapshot) if persist else None
    findings = derive_m01_passive_findings(snapshot)
    return {
        "module_id": "m01_osint",
        "snapshot": snapshot.to_dict(),
        "artifact_path": artifact_path.as_posix() if artifact_path else None,
        "findings": [finding.to_dict() for finding in findings],
        "finding_count": len(findings),
        "execution_scope": "passive_dns_only",
    }


@router.get("/api/ops/m16/windows-start-plan")
def get_m16_windows_start_plan() -> dict[str, Any]:
    """Return a plain-language Windows start plan connected to real project scripts and APIs."""
    readiness = build_m16_readiness_report(env=_settings_to_m16_env())
    m01_module = get_module_by_id("m01_osint")
    return {
        "status": readiness.status,
        "main_windows_entrypoint": "scripts\\windows\\iniciar_ojo_de_dios_windows.bat",
        "m16_ai_entrypoint": "scripts\\windows\\ia\\instalar_modulo16_completo.bat",
        "open_in_browser": "http://127.0.0.1:8000/modules",
        "m01_ready_for_passive_dns": m01_module is not None,
        "m01_passive_dns_api": "/api/modules/m01_osint/osint/domain-snapshot",
        "what_this_does": [
            "prepara Python y dependencias locales",
            "arranca la aplicacion web",
            "deja Mistral/Ollama y Hermes Agent como instalacion Windows separada",
            "conecta el modulo 16 con el catalogo y con el modulo 1",
        ],
        "readiness": readiness.to_dict(),
    }


@router.get("/api/ops/m16/first-run")
def get_m16_first_run() -> dict[str, Any]:
    """Return local GitHub ZIP first-run preflight status without external calls."""
    report = build_first_run_report()
    return {"first_run": report.to_dict()}


@router.post("/api/ops/m16/first-run/write")
def write_m16_first_run() -> dict[str, Any]:
    """Persist local GitHub ZIP first-run preflight status."""
    report = build_first_run_report()
    status_path = write_first_run_status(report)
    return {"first_run": report.to_dict(), "status_path": status_path.relative_to(Path.cwd()).as_posix() if status_path.is_absolute() and Path.cwd() in status_path.parents else status_path.as_posix()}


@router.get("/api/ops/m16/windows-station-manifest")
def get_m16_windows_station_manifest() -> dict[str, Any]:
    """Return the complete local Windows handoff manifest for M16."""
    return {"station_manifest": build_windows_station_manifest()}


@router.get("/api/ops/m16/readiness")
def get_m16_readiness() -> dict[str, Any]:
    """Return M16 readiness without persisting runtime state."""
    report = build_m16_readiness_report(env=_settings_to_m16_env())
    return {"readiness": report.to_dict()}


@router.get("/api/ops/m16/readiness/history")
def get_m16_readiness_history(limit: int = 50) -> dict[str, Any]:
    """Return persisted M16 readiness observations and degraded-state alerts."""
    return {"readiness_history": read_m16_readiness_history(limit=limit)}


@router.get("/api/ops/m16/local-ai-health")
def get_m16_local_ai_health(client: MistralClient = Depends(get_local_mistral_client)) -> dict[str, Any]:
    """Query the configured local Ollama catalog and report Mistral model availability."""
    try:
        probe = client.probe()
    except ConfigurationError as exc:
        return {
            "status": "UNAVAILABLE",
            "model": client.model,
            "detail": str(exc),
            "inference_performed": False,
        }
    return {
        "status": "READY" if probe["model_available"] else "MODEL_MISSING",
        "model": client.model,
        "probe": probe,
    }


@router.post("/api/ops/m16/readiness/write")
def write_m16_readiness() -> dict[str, Any]:
    """Build and persist an M16 readiness snapshot in storage/runtime."""
    report = build_m16_readiness_report(env=_settings_to_m16_env())
    status_path = write_runtime_status(report)
    return {
        "readiness": report.to_dict(),
        "runtime_status_path": status_path.relative_to(Path.cwd()).as_posix() if status_path.is_absolute() and Path.cwd() in status_path.parents else status_path.as_posix(),
    }


@router.post("/api/ops/m16/actions/{action_id}")
def run_m16_guided_action(action_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run one guided M16 control-center action and return an auditable result."""
    result = run_m16_operational_action(
        action_id,
        parameters=payload or {},
        repo_root=Path.cwd(),
        env=_settings_to_m16_env(),
    )
    return {"result": result.to_dict()}


@router.get("/api/ops/knowledge/status")
def get_knowledge_base_status() -> dict[str, Any]:
    """Return the auditable local knowledge status manifest without rebuilding it."""
    try:
        status = read_knowledge_status()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Knowledge base has not been built.") from exc
    return {"knowledge_status": status}


@router.post("/api/ops/knowledge/build")
def build_knowledge_base_api(payload: dict[str, Any]) -> dict[str, Any]:
    """Build local knowledge artifacts after explicit operator confirmation."""
    if payload.get("execute_build") is not True:
        raise HTTPException(status_code=400, detail="Knowledge build requires execute_build=true.")
    mode = str(payload.get("mode", "docs-only"))
    if mode not in {"docs-only", "semantic"}:
        raise HTTPException(status_code=400, detail="Knowledge build mode must be docs-only or semantic.")
    try:
        status = build_knowledge_base(repo_root=Path.cwd(), output_dir=Path("storage/knowledge"), mode=mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "mode": "local_knowledge_build",
        "external_api_call_performed": False,
        "model_download_performed": False,
        "knowledge_status": status,
    }


@router.get("/api/ops/knowledge/search")
def search_knowledge_base_api(q: str, limit: int = 5) -> dict[str, Any]:
    """Search the local knowledge artifacts with deterministic lexical matching."""
    try:
        search = search_knowledge_base(query=q, limit=limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Knowledge base has not been built.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"search": search}


@router.get("/api/ops/knowledge/context-pack")
def get_knowledge_context_pack_api(q: str, limit: int = 5) -> dict[str, Any]:
    """Return a bounded local knowledge context pack for LaIA/Hermes prompts."""
    try:
        context_pack = build_knowledge_context_pack(query=q, limit=limit)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Knowledge base has not been built.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"context_pack": context_pack}


@router.get("/api/ops/toolhealth/python-runtime")
def get_python_runtime_toolhealth() -> dict[str, Any]:
    """Return ToolHealth for the current Python runtime used by Ojo de Dios."""
    return {"tool_health": check_python_tool_health().details}


@router.post("/api/ai/hermes/assist/request-preview")
def preview_hermes_assist_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Build a DeepSeek/Hermes request preview without calling external AI."""
    settings = get_settings()
    augmented_payload = _knowledge_augmented_hermes_payload(payload)
    request = _hermes_assist_request_from_payload(augmented_payload, settings.deepseek_model)
    try:
        deepseek_request = build_hermes_deepseek_chat_request(request, settings)
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "mode": "hermes_deepseek_request_preview_no_external_call",
        "deepseek_request": deepseek_request.to_payload(),
        "external_ai_call_performed": False,
        "configured_model": settings.deepseek_model,
        "configured_pro_model": settings.deepseek_pro_model,
    }


@router.post("/api/ai/hermes/assist")
def run_hermes_assist(
    payload: dict[str, Any],
    service: HermesDeepSeekAssistService = Depends(get_hermes_assist_service),
) -> dict[str, Any]:
    """Execute a gated Hermes/DeepSeek assist call only after explicit external-AI approval."""
    if payload.get("execute_external_ai") is not True:
        raise HTTPException(status_code=400, detail="Hermes assist requires execute_external_ai=true.")
    augmented_payload = _knowledge_augmented_hermes_payload(payload)
    request = _hermes_assist_request_from_payload(augmented_payload, service.settings.deepseek_model)
    try:
        response = service.ask_json(request)
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    receipt = write_hermes_assist_receipt(request, response)
    return {"hermes_assist": response.to_dict(), "receipt": receipt.to_dict()}


@router.get("/api/ai/hermes/assist/receipts")
def list_hermes_assist_receipt_api() -> dict[str, Any]:
    """Return persisted, redacted Hermes assist receipts in stable order."""
    receipts = [receipt.to_dict() for receipt in list_hermes_assist_receipts()]
    return {"receipts": receipts, "count": len(receipts)}


@router.get("/api/ai/hermes/assist/receipts/summary")
def summarize_hermes_assist_receipt_api() -> dict[str, Any]:
    """Return aggregate audit metadata for persisted Hermes assist receipts."""
    return {"summary": summarize_hermes_assist_receipts()}


@router.get("/api/ai/hermes/assist/receipts/{receipt_id}/context-pack")
def get_hermes_assist_receipt_context_pack_api(receipt_id: str) -> dict[str, Any]:
    """Return a bounded, redacted local-AI context pack for one Hermes assist receipt."""
    try:
        context_pack = build_hermes_receipt_context_pack(receipt_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Hermes assist receipt not found.") from exc
    return {"context_pack": context_pack}


@router.get("/api/ai/hermes/assist/receipts/{receipt_id}/prompt-envelope")
def get_hermes_assist_receipt_prompt_envelope_api(receipt_id: str) -> dict[str, Any]:
    """Return a local prompt envelope for reviewing one Hermes assist receipt."""
    try:
        prompt_envelope = build_hermes_receipt_prompt_envelope(receipt_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Hermes assist receipt not found.") from exc
    return {"prompt_envelope": prompt_envelope}


@router.get("/api/ai/hermes/assist/receipts/{receipt_id}/chatml-prompt")
def get_hermes_assist_receipt_chatml_prompt_api(receipt_id: str) -> dict[str, Any]:
    """Return a ChatML prompt for local Dolphin Mistral review of one Hermes receipt."""
    try:
        prompt = render_hermes_receipt_chatml_prompt(receipt_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Hermes assist receipt not found.") from exc
    return {"chatml_prompt": prompt}


@router.post("/api/ai/hermes/assist/receipts/{receipt_id}/laia-review")
def run_laia_review_for_hermes_receipt_api(
    receipt_id: str,
    payload: dict[str, Any],
    client: MistralClient = Depends(get_local_mistral_client),
) -> dict[str, Any]:
    """Run a gated local LaIA/Mistral review for one Hermes assist receipt."""
    if payload.get("execute_local_ai") is not True:
        raise HTTPException(status_code=400, detail="LaIA receipt review requires execute_local_ai=true.")
    try:
        prompt = render_hermes_receipt_chatml_prompt(receipt_id)
        review_text = client.generate_text(prompt["prompt"])
        safe_review_text = str(redact_hermes_payload(review_text))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Hermes assist receipt not found.") from exc
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    review_receipt = write_laia_receipt_review(
        source_receipt_id=receipt_id,
        model=client.model,
        prompt_sha256=str(prompt["prompt_sha256"]),
        content=safe_review_text,
    )
    return {
        "mode": "laia_mistral_hermes_receipt_review",
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
        "model": client.model,
        "receipt_id": receipt_id,
        "prompt_sha256": prompt["prompt_sha256"],
        "content": safe_review_text,
        "review_receipt": review_receipt.to_dict(),
    }


@router.get("/api/ai/hermes/assist/receipts/{receipt_id}/laia-reviews")
def list_laia_reviews_for_hermes_receipt_api(receipt_id: str) -> dict[str, Any]:
    """Return persisted local LaIA review receipts for one Hermes assist receipt."""
    reviews = [review.to_dict() for review in list_laia_receipt_reviews(source_receipt_id=receipt_id)]
    return {"reviews": reviews, "count": len(reviews), "receipt_id": receipt_id}


@router.get("/api/ai/hermes/assist/laia-reviews/summary")
def summarize_laia_receipt_reviews_api(source_receipt_id: str | None = None) -> dict[str, Any]:
    """Return aggregate metadata for persisted local LaIA review receipts."""
    return {"summary": summarize_laia_receipt_reviews(source_receipt_id=source_receipt_id)}


@router.get("/api/ai/hermes/assist/laia-reviews/{review_id}/context-pack")
def get_laia_receipt_review_context_pack_api(review_id: str) -> dict[str, Any]:
    """Return a bounded context pack for one persisted local LaIA review receipt."""
    try:
        context_pack = build_laia_receipt_review_context_pack(review_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="LaIA receipt review not found.") from exc
    return {"context_pack": context_pack}


@router.get("/api/ai/hermes/assist/laia-reviews/{review_id}/prompt-envelope")
def get_laia_receipt_review_prompt_envelope_api(review_id: str) -> dict[str, Any]:
    """Return a prompt envelope for auditing one persisted local LaIA review receipt."""
    try:
        prompt_envelope = build_laia_receipt_review_prompt_envelope(review_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="LaIA receipt review not found.") from exc
    return {"prompt_envelope": prompt_envelope}


@router.get("/api/ai/hermes/assist/laia-reviews/{review_id}/chatml-prompt")
def get_laia_receipt_review_chatml_prompt_api(review_id: str) -> dict[str, Any]:
    """Return a ChatML prompt for auditing one persisted local LaIA review receipt."""
    try:
        chatml_prompt = render_laia_receipt_review_chatml_prompt(review_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="LaIA receipt review not found.") from exc
    return {"chatml_prompt": chatml_prompt}


@router.post("/api/ai/hermes/assist/laia-reviews/{review_id}/audit")
def run_laia_review_receipt_audit_api(
    review_id: str,
    payload: dict[str, Any],
    client: MistralClient = Depends(get_local_mistral_client),
) -> dict[str, Any]:
    """Run a gated local LaIA/Mistral second-pass audit for one LaIA review receipt."""
    if payload.get("execute_local_ai") is not True:
        raise HTTPException(status_code=400, detail="LaIA review receipt audit requires execute_local_ai=true.")
    try:
        prompt = render_laia_receipt_review_chatml_prompt(review_id)
        audit_text = client.generate_text(prompt["prompt"])
        safe_audit_text = str(redact_hermes_payload(audit_text))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="LaIA receipt review not found.") from exc
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    audit_receipt = write_laia_review_receipt_audit(
        source_review_id=review_id,
        source_receipt_id=str(prompt["source_receipt_id"]),
        model=client.model,
        prompt_sha256=str(prompt["prompt_sha256"]),
        content=safe_audit_text,
    )
    return {
        "mode": "laia_mistral_review_receipt_audit",
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
        "model": client.model,
        "review_id": review_id,
        "source_receipt_id": prompt["source_receipt_id"],
        "prompt_sha256": prompt["prompt_sha256"],
        "content": safe_audit_text,
        "audit_receipt": audit_receipt.to_dict(),
    }


@router.get("/api/ai/hermes/assist/laia-reviews/{review_id}")
def get_laia_receipt_review_api(review_id: str) -> dict[str, Any]:
    """Return one persisted local LaIA review receipt by id."""
    try:
        review = read_laia_receipt_review(review_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="LaIA receipt review not found.") from exc
    return {"review": review.to_dict()}


@router.get("/api/ai/hermes/assist/receipts/{receipt_id}")
def get_hermes_assist_receipt_api(receipt_id: str) -> dict[str, Any]:
    """Return one persisted, redacted Hermes assist receipt by id."""
    try:
        receipt = read_hermes_assist_receipt(receipt_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Hermes assist receipt not found.") from exc
    return {"receipt": receipt.to_dict()}


@router.get("/api/ai/modules/context-pack")
def get_ai_module_context_pack(include_reserved: bool = True) -> dict[str, Any]:
    """Return bounded module context for LaIA/Mistral without invoking an LLM."""
    return {"context_pack": build_module_context_pack(include_reserved=include_reserved).to_dict()}


@router.get("/api/ai/modules/{module_id}/explain")
def get_ai_module_explanation(module_id: str) -> dict[str, Any]:
    """Return deterministic module explanation context for LaIA/Mistral."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"module_explanation": explain_module_for_ai(module_id)}


@router.get("/api/ai/modules/{module_id}/prompt-envelope")
def get_ai_module_prompt_envelope(module_id: str) -> dict[str, Any]:
    """Return prompt-ready LaIA/Mistral envelope without invoking an LLM."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"prompt_envelope": build_module_prompt_envelope(module_id).to_dict()}


@router.get("/api/ai/modules/{module_id}/install/context-pack")
def get_ai_tool_install_context_pack(module_id: str) -> dict[str, Any]:
    """Return bounded install-plan context for AI review without executing tools."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return {"context_pack": build_tool_install_context_pack(module_id).to_dict()}


@router.get("/api/ai/modules/{module_id}/tool-runs/{run_id}/context-pack")
def get_ai_tool_run_context_pack(
    module_id: str,
    run_id: str,
    tool_id: str,
    max_artifacts: int = 10,
    max_payload_bytes: int = 64_000,
) -> dict[str, Any]:
    """Return bounded tool-run context for LaIA/Mistral without invoking an LLM."""
    if get_module_by_id(module_id) is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        context_pack = build_tool_run_context_pack(
            module_id,
            tool_id,
            run_id,
            max_artifacts=max_artifacts,
            max_payload_bytes=max_payload_bytes,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Tool run not found.") from exc
    return {"context_pack": context_pack.to_dict()}
