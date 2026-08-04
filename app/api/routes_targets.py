"""Target API routes for Ojo de Dios."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.contracts.job_contract import JOB_MODE_DRY_RUN, JOB_STATUS_FAILED, JobResult
from app.contracts.evidence_contract import RESULT_FAILED
from app.ai.m01_context import (
    build_m01_target_context_pack,
    build_m01_target_prompt_envelope,
    list_m01_target_ai_reviews,
    render_m01_target_chatml_prompt,
    write_m01_target_ai_review,
)
from app.ai.module_context import (
    build_target_module_context_pack,
    list_target_module_ai_reviews,
    render_target_module_chatml_prompt,
    write_target_module_ai_review,
)
from app.core.m01_action_plan import build_m01_action_plan, write_m01_action_plan
from app.core.m01_action_tracking import build_m01_action_board, update_m01_action_progress
from app.core.m02_vulnerability_inventory import (
    read_m02_service_inventory,
    service_observation_from_payload,
    write_m02_service_inventory,
)
from app.core.m03_service_mapping import build_m03_service_map, read_m03_service_map, write_m03_service_map
from app.core.m04_web_baseline import read_m04_web_baseline, web_response_observation_from_payload, write_m04_web_baseline
from app.core.m05_credential_evidence import (
    credential_evidence_from_payload,
    list_m05_credential_evidence,
    verify_m05_credential_material,
    write_m05_credential_evidence,
)
from app.core.m06_capture_evidence import list_m06_capture_evidence, write_m06_capture_evidence
from app.core.m07_session_evidence import list_m07_session_evidence, session_evidence_from_payload, write_m07_session_evidence
from app.core.m08_resilience_metrics import measurement_from_payload, read_m08_resilience_measurements, write_m08_resilience_measurements
from app.core.m09_intelligence_dataset import normalize_intelligence_record, read_m09_intelligence_dataset, write_m09_intelligence_dataset
from app.core.m10_radio_observations import radio_observation_from_payload, read_m10_radio_observations, write_m10_radio_observations
from app.core.m11_device_inventory import device_observation_from_payload, read_m11_device_inventory, write_m11_device_inventory
from app.core.m12_evidence_ledger import build_m12_evidence_ledger, read_m12_evidence_ledger, write_m12_evidence_ledger
from app.core.m13_android_apk_evidence import list_m13_apk_evidence, write_m13_apk_evidence
from app.core.m14_awareness_campaign import (
    awareness_campaign_from_payload,
    read_m14_awareness_campaigns,
    write_m14_awareness_campaign,
    write_m14_awareness_outcomes,
)
from app.core.m15_cloud_inventory import cloud_asset_from_payload, read_m15_cloud_inventory, write_m15_cloud_inventory
from app.ai.mistral_client import MistralClient
from app.config import get_settings
from app.core.errors import ConfigurationError, ContractError
from app.core.attack_surface_graph import build_attack_surface_graph
from app.core.evidence_store import EvidenceStore
from app.core.job_runtime_control import write_job_stop_request
from app.core.module_action_plan import (
    build_module_action_board,
    build_module_action_plan,
    update_module_action_progress,
    write_module_action_plan,
)
from app.core.module_findings import derive_target_module_findings
from app.core.module_run_result import build_target_module_run_result
from app.core.ojo_router import OjoRouter
from app.core.runtime_registry import RuntimeRegistrySnapshot, get_runtime_registry_snapshot
from app.core.service_fingerprint import build_service_fingerprint_report
from app.core.target_fingerprint import TargetFingerprint, build_target_fingerprint
from app.core.target_model import TARGET_MODE_DRY_RUN, TargetRecord, TargetRequest
from app.core.target_operations_summary import build_target_operations_summary
from app.core.target_osint import list_target_passive_dns_history, run_target_passive_dns
from app.core.target_workspace import (
    bind_target_module_workspace,
    catalog_module_ids_from_allowed_modules,
    collect_target_workspace_state,
    ensure_target_workspace,
)
from app.core.x5_strategy_engine import StrategyPlan, StrategyPlanStep
from app.db.models import Target, TargetFingerprintModel
from app.db.repositories.jobs_repository import JobsRepository
from app.db.repositories.targets_repository import TargetsRepository
from app.db.session import get_session
from app.workers.job_runner import JobRunner

router = APIRouter()


def get_target_mistral_client() -> MistralClient:
    """Build the configured local Mistral client for target-scoped AI review."""
    settings = get_settings()
    return MistralClient(
        base_url=settings.ollama_base_url,
        model=settings.mistral_model,
        timeout_seconds=settings.mistral_timeout_seconds,
        enabled=settings.ai_enabled and settings.mistral_enabled,
    )


class TargetCreateRequest(BaseModel):
    """Payload for target creation."""

    name: str
    target_type: str
    value: str
    mode: str = TARGET_MODE_DRY_RUN
    allowed_modules: list[str] = Field(default_factory=list)
    limits: dict[str, Any] = Field(default_factory=dict)
    noise_profile: str = "normal"
    evidence_profile: str = "standard"
    require_confirmations: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class TargetWorkspaceBindRequest(BaseModel):
    """Payload for creating a target workspace and module bindings."""

    module_ids: list[str] = Field(default_factory=list)
    bind_allowed_modules: bool = True


class M01ActionProgressRequest(BaseModel):
    """Explicit operator update for one current M01 evidence-derived action."""

    step_id: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=32)
    note: str = Field(default="", max_length=4000)


class ModuleActionProgressRequest(BaseModel):
    """Explicit operator update for one current module evidence-derived action."""

    step_id: str = Field(min_length=1, max_length=128)
    status: str = Field(min_length=1, max_length=32)
    note: str = Field(default="", max_length=4000)


class M02ServiceInventoryRequest(BaseModel):
    """Operator-provided M02 service evidence and optional public advisory lookup flag."""

    services: list[dict[str, Any]] = Field(min_length=1, max_length=100)
    fetch_external: bool = False


class M04WebBaselineRequest(BaseModel):
    """Approved, already-observed HTTP metadata; never causes the server to request a URL."""

    url: str = Field(min_length=1, max_length=512)
    status_code: int = Field(ge=100, le=599)
    headers: dict[str, str] = Field(default_factory=dict)
    source: str = Field(default="operator_observed", min_length=1, max_length=512)
    evidence_ref: str | None = Field(default=None, max_length=512)


class M05CredentialEvidenceRequest(BaseModel):
    """Transient secret material is fingerprinted and deliberately never persisted."""

    credential_type: str = Field(min_length=1, max_length=64)
    label: str = Field(min_length=1, max_length=512)
    secret_material: str = Field(min_length=1, max_length=16_384)
    source: str = Field(default="operator_provided", min_length=1, max_length=512)
    evidence_ref: str | None = Field(default=None, max_length=512)


class M05CredentialVerificationRequest(BaseModel):
    """Transient material to compare locally with the selected evidence receipt."""

    secret_material: str = Field(min_length=1, max_length=16_384)


class M07SessionEvidenceRequest(BaseModel):
    """Metadata-only record of an already authorised session; no session secret field exists."""

    session_reference: str = Field(min_length=1, max_length=512)
    host_label: str = Field(min_length=1, max_length=512)
    platform: str = Field(min_length=1, max_length=512)
    privilege_level: str = Field(default="unknown", max_length=64)
    state: str = Field(default="observed", max_length=64)
    source: str = Field(default="operator_observed", min_length=1, max_length=512)
    evidence_ref: str | None = Field(default=None, max_length=512)


class M08ResilienceMeasurementsRequest(BaseModel):
    """Observed monitoring measurements; this endpoint cannot initiate a load test."""

    measurements: list[dict[str, Any]] = Field(min_length=1, max_length=10_000)


class M09IntelligenceDatasetRequest(BaseModel):
    """Already collected records to normalize; this API never invokes a scraper or connector."""

    records: list[dict[str, Any]] = Field(min_length=1, max_length=5_000)


class M10RadioObservationsRequest(BaseModel):
    """Passive observations supplied by the operator; cannot start RF capture or transmission."""

    observations: list[dict[str, Any]] = Field(min_length=1, max_length=10_000)


class M11DeviceInventoryRequest(BaseModel):
    """Observed device metadata; transient identifiers are fingerprinted before storage."""

    observations: list[dict[str, Any]] = Field(min_length=1, max_length=10_000)


class M15CloudInventoryRequest(BaseModel):
    """Cloud, container, or Kubernetes records exported by the operator."""

    assets: list[dict[str, Any]] = Field(min_length=1, max_length=10_000)


class M14AwarenessCampaignRequest(BaseModel):
    """Definition for a privacy-preserving awareness training campaign."""

    campaign_name: str = Field(min_length=1, max_length=512)
    channel: str = Field(min_length=1, max_length=64)
    subject: str = Field(default="Awareness training", min_length=1, max_length=512)
    body: str = Field(min_length=1, max_length=8_000)
    training_url: str = Field(min_length=1, max_length=2_048)
    recipients: list[str] = Field(min_length=1, max_length=20_000)
    owner: str = Field(default="local_operator", min_length=1, max_length=512)


class M14AwarenessOutcomesRequest(BaseModel):
    """Imported outcomes for an existing M14 awareness campaign."""

    outcomes: list[dict[str, Any]] = Field(min_length=1, max_length=20_000)


class TargetJobStartRequest(BaseModel):
    """Payload for starting a target job through the local JobRunner."""

    mode: str = JOB_MODE_DRY_RUN
    selected_modules: list[str] = Field(default_factory=list)
    selected_techniques: list[str] = Field(default_factory=list)
    confirmed: bool = False
    allowlisted_target: bool = True
    hardware_available: bool = True
    network_available: bool = True
    user_logic_available: bool = False
    parameters: dict[str, Any] = Field(default_factory=dict)
    created_by: str = "local_operator"


def _load_json(value: str) -> Any:
    return json.loads(value)


def _target_to_payload(target: Target) -> dict[str, Any]:
    return {
        "target_id": target.target_id,
        "name": target.name,
        "target_type": target.target_type,
        "value": target.value,
        "normalized_value": target.normalized_value,
        "mode": target.mode,
        "allowed_modules": _load_json(target.allowed_modules_json),
        "limits": _load_json(target.limits_json),
        "noise_profile": target.noise_profile,
        "evidence_profile": target.evidence_profile,
        "require_confirmations": target.require_confirmations,
        "metadata": _load_json(target.metadata_json),
        "created_by": target.created_by,
        "created_at": target.created_at.isoformat() if target.created_at else None,
    }


def _fingerprint_to_payload(fingerprint: TargetFingerprintModel | None) -> dict[str, Any] | None:
    if fingerprint is None:
        return None
    return {
        "target_id": fingerprint.target_id,
        "target_type": fingerprint.target_type,
        "original_value": fingerprint.original_value,
        "normalized_value": fingerprint.normalized_value,
        "fingerprint": _load_json(fingerprint.fingerprint_json),
        "tags": _load_json(fingerprint.tags_json),
        "confidence": fingerprint.confidence,
        "created_at": fingerprint.created_at.isoformat() if fingerprint.created_at else None,
    }


def _fingerprint_model_to_contract(fingerprint: TargetFingerprintModel) -> TargetFingerprint:
    return TargetFingerprint(
        target_id=fingerprint.target_id,
        target_type=fingerprint.target_type,
        original_value=fingerprint.original_value,
        normalized_value=fingerprint.normalized_value,
        fingerprint=_load_json(fingerprint.fingerprint_json),
        tags=_load_json(fingerprint.tags_json),
        confidence=fingerprint.confidence,
    )


def _target_to_record(target: Target) -> TargetRecord:
    """Convert a database target into the core planning contract."""
    return TargetRecord(
        target_id=target.target_id,
        name=target.name,
        target_type=target.target_type,
        value=target.value,
        normalized_value=target.normalized_value,
        mode=target.mode,
        allowed_modules=_load_json(target.allowed_modules_json),
        limits=_load_json(target.limits_json),
        noise_profile=target.noise_profile,
        evidence_profile=target.evidence_profile,
        require_confirmations=target.require_confirmations,
        metadata=_load_json(target.metadata_json),
        created_by=target.created_by,
        created_at=target.created_at.isoformat() if target.created_at else None,
    )


def _plan_step_to_payload(step: StrategyPlanStep) -> dict[str, Any]:
    return {
        "step": step.step,
        "technique_id": step.technique_id,
        "module_id": step.module_id,
        "display_name": step.display_name,
        "implementation_status": step.implementation_status,
        "permission_level": step.permission_level,
        "requires_confirmation": step.requires_confirmation,
        "requires_user_logic": step.requires_user_logic,
        "can_run_now": step.can_run_now,
        "blocked_reason": step.blocked_reason,
        "reason": step.reason,
        "expected_evidence": step.expected_evidence,
        "required_inputs": step.required_inputs,
        "missing_inputs": step.missing_inputs,
    }


def _plan_to_payload(plan: StrategyPlan) -> dict[str, Any]:
    return {
        "target_id": plan.target_id,
        "target_type": plan.target_type,
        "mode": plan.mode,
        "status": plan.status,
        "reason": plan.reason,
        "step_count": len(plan.steps),
        "runnable_step_count": plan.runnable_step_count,
        "blocked_step_count": plan.blocked_step_count,
        "can_execute": plan.can_execute,
        "blocked_reasons": plan.blocked_reasons,
        "steps": [_plan_step_to_payload(step) for step in plan.steps],
    }


def _job_to_payload(job) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "target_id": job.target_id,
        "created_by": job.created_by,
        "mode": job.mode,
        "selected_modules": _load_json(job.selected_modules_json),
        "selected_techniques": _load_json(job.selected_techniques_json),
        "status": job.status,
        "result_status": job.result_status,
        "evidence_ids": _load_json(job.evidence_ids_json),
        "summary": job.summary,
        "error": job.error,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }


def _stored_evidence_to_payload(stored) -> dict[str, Any]:
    return {
        "evidence_id": stored.evidence_id,
        "run_id": stored.run_id,
        "target_id": stored.target_id,
        "technique_id": stored.technique_id,
        "module_id": stored.module_id,
        "evidence_type": stored.evidence_type,
        "quality": stored.quality,
        "summary": stored.summary,
        "source": stored.source,
        "content_hash": stored.content_hash,
        "content_path": stored.content_path,
        "demo": stored.demo,
        "real_execution": stored.real_execution,
        "created_at": stored.created_at,
    }


def _stored_evidence_to_payloads(
    stored_items: list[Any],
    store: EvidenceStore,
    verify_content: bool = False,
) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []
    for stored in stored_items:
        item = _stored_evidence_to_payload(stored)
        if verify_content:
            content_result = store.read_content_result(stored.evidence_id)
            item["content_hash_verified"] = content_result.verified
            item["content_read_status"] = "verified" if content_result.verified else "unverified"
            item["content_read_error"] = content_result.failure_reason
        payloads.append(item)
    return payloads


def _stored_evidence_summary(stored) -> dict[str, Any]:
    return {
        "evidence_id": stored.evidence_id,
        "run_id": stored.run_id,
        "technique_id": stored.technique_id,
        "module_id": stored.module_id,
        "evidence_type": stored.evidence_type,
        "quality": stored.quality,
        "summary": stored.summary,
        "created_at": stored.created_at,
    }


def _stored_module_findings(store: EvidenceStore, target_id: str, module_id: str) -> tuple[list[dict[str, Any]], int, int]:
    stored_items = store.list_target_module(target_id, module_id, limit=500)
    findings_by_id: dict[str, dict[str, Any]] = {}
    unverified_count = 0
    for stored in stored_items:
        content_result = store.read_content_result(stored.evidence_id)
        if not content_result.verified:
            unverified_count += 1
            continue
        payload = content_result.content
        if not isinstance(payload, dict):
            continue
        candidate_payloads = [payload]
        content = payload.get("content")
        if isinstance(content, dict):
            candidate_payloads.append(content)
        for candidate in candidate_payloads:
            for finding in derive_target_module_findings(module_id, candidate):
                item = finding.to_dict()
                refs = [str(ref) for ref in item.get("evidence_refs", []) if ref]
                evidence_ref = f"evidence_store:{stored.evidence_id}"
                if evidence_ref not in refs:
                    refs.append(evidence_ref)
                item["evidence_refs"] = refs
                findings_by_id[str(item["finding_id"])] = item
    return list(findings_by_id.values()), len(stored_items), unverified_count


def _selected_techniques_from_payload_or_plan(payload: TargetJobStartRequest, plan: StrategyPlan) -> list[str]:
    if payload.selected_techniques:
        return list(payload.selected_techniques)
    return [step.technique_id for step in plan.runnable_steps]


def _start_blocked_response(target: Target, plan: StrategyPlan, reason: str) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={
            "status": "start_blocked",
            "reason": reason,
            "target": _target_to_payload(target),
            "plan": _plan_to_payload(plan),
            "execution_started": False,
        },
    )


def _require_target(repository: TargetsRepository, target_id: str) -> Target:
    target = repository.get_by_target_id(target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found.")
    return target


def _select_workspace_module_ids(target_record: TargetRecord, payload: TargetWorkspaceBindRequest) -> tuple[str, ...]:
    selected: list[str] = []
    if payload.bind_allowed_modules:
        selected.extend(catalog_module_ids_from_allowed_modules(target_record.allowed_modules))
    for module_id in payload.module_ids:
        if module_id not in selected:
            selected.append(module_id)
    return tuple(selected)


def _not_available(reason: str) -> JSONResponse:
    return JSONResponse(
        status_code=501,
        content={
            "status": "not_available_yet",
            "reason": reason,
        },
    )


def _runtime_registry_payload(snapshot: RuntimeRegistrySnapshot) -> dict[str, object]:
    """Return runtime registry status for target planning responses."""
    return snapshot.to_status_payload()


def _runtime_router() -> tuple[OjoRouter, RuntimeRegistrySnapshot]:
    """Build an OjoRouter from the concrete runtime registry snapshot."""
    snapshot = get_runtime_registry_snapshot()
    return OjoRouter(snapshot.registry), snapshot


def _module_run_payload(
    target: Target,
    module_id: str,
    run_type: str,
    artifact_path: str,
    payload: dict[str, Any] | None = None,
    flags: dict[str, object] | None = None,
) -> dict[str, object]:
    """Build the shared module-run envelope returned by target-scoped module writes."""
    artifact_payload = payload
    if artifact_payload is None:
        try:
            loaded = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            loaded = None
        artifact_payload = loaded if isinstance(loaded, dict) else None
    findings = derive_target_module_findings(module_id, artifact_payload)
    merged_flags = dict(flags or {})
    if findings:
        merged_flags["finding_ids"] = [finding.finding_id for finding in findings]
    return build_target_module_run_result(
        target_id=target.target_id,
        module_id=module_id,
        run_type=run_type,
        artifact_path=artifact_path,
        finding_count=len(findings),
        payload=artifact_payload,
        flags=merged_flags,
    ).to_dict()


def _module_findings_payload(
    module_id: str,
    payload: dict[str, Any] | None,
    artifact_path: str | None = None,
) -> list[dict[str, object]]:
    """Return evidence-derived findings for the same payload used by module_run."""
    artifact_payload = payload
    if artifact_payload is None and artifact_path:
        try:
            loaded = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            loaded = None
        artifact_payload = loaded if isinstance(loaded, dict) else None
    return [finding.to_dict() for finding in derive_target_module_findings(module_id, artifact_payload)]


@router.post("/api/targets/create")
def create_target(payload: TargetCreateRequest, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Create a target and its initial local fingerprint."""
    repository = TargetsRepository(session)
    request = TargetRequest(
        name=payload.name,
        target_type=payload.target_type,
        value=payload.value,
        mode=payload.mode,
        allowed_modules=payload.allowed_modules,
        limits=payload.limits,
        noise_profile=payload.noise_profile,
        evidence_profile=payload.evidence_profile,
        require_confirmations=payload.require_confirmations,
        metadata=payload.metadata,
    )
    try:
        target = repository.create_target(request)
        fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)
        stored_fingerprint = repository.create_fingerprint(fingerprint)
    except ContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "target": _target_to_payload(target),
        "fingerprint": _fingerprint_to_payload(stored_fingerprint),
    }


@router.post("/api/targets/{target_id}/m01/passive-dns")
def run_target_m01_passive_dns(
    target_id: str,
    include_external: bool = Query(False),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Run M01 passive DNS for a stored domain/url target and persist target-bound evidence."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        result = run_target_passive_dns(_target_to_record(target), include_external=include_external)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"m01_passive_dns": result.to_dict()}


@router.get("/api/targets/{target_id}/m01/passive-dns/history")
def get_target_m01_passive_dns_history(
    target_id: str, limit: int = Query(10, ge=1, le=50), session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Return persisted M01 passive DNS history for a stored target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    history = list_target_passive_dns_history(_target_to_record(target), limit=limit)
    return {
        "target_id": target_id,
        "history": [entry.to_dict() for entry in history],
        "history_count": len(history),
    }


@router.get("/api/targets/{target_id}/operations-summary")
def get_target_operations_summary(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return a target-wide rollup of persisted module artifacts, findings, actions and reviews."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    summary_payload = build_target_operations_summary(_target_to_record(target)).to_dict()
    stored_evidence = EvidenceStore(session).list_target(target_id, limit=500)
    evidence_by_module: dict[str, int] = {}
    latest_evidence_by_module: dict[str, dict[str, Any]] = {}
    stored_finding_count_by_module: dict[str, int] = {}
    unverified_evidence_count_by_module: dict[str, int] = {}
    for item in stored_evidence:
        evidence_by_module[item.module_id] = evidence_by_module.get(item.module_id, 0) + 1
        latest_evidence_by_module.setdefault(item.module_id, _stored_evidence_summary(item))
    evidence_store = EvidenceStore(session)
    for module in summary_payload["modules"]:
        if isinstance(module, dict):
            module_id = str(module.get("module_id"))
            stored_findings, _stored_count, stored_unverified_count = _stored_module_findings(evidence_store, target_id, module_id)
            stored_finding_count = len(stored_findings)
            stored_finding_count_by_module[module_id] = stored_finding_count
            unverified_evidence_count_by_module[module_id] = stored_unverified_count
            module["stored_evidence_count"] = evidence_by_module.get(module_id, 0)
            module["unverified_stored_evidence_count"] = stored_unverified_count
            module["stored_evidence_finding_count"] = stored_finding_count
            module["effective_finding_count"] = int(module.get("finding_count") or 0) + stored_finding_count
            module["latest_stored_evidence"] = latest_evidence_by_module.get(module_id)
    summary_payload["stored_evidence_count"] = len(stored_evidence)
    summary_payload["stored_evidence_by_module"] = evidence_by_module
    summary_payload["stored_evidence_finding_count"] = sum(stored_finding_count_by_module.values())
    summary_payload["stored_evidence_finding_count_by_module"] = stored_finding_count_by_module
    summary_payload["unverified_stored_evidence_count"] = sum(unverified_evidence_count_by_module.values())
    summary_payload["unverified_stored_evidence_count_by_module"] = unverified_evidence_count_by_module
    summary_payload["effective_finding_count"] = int(summary_payload.get("finding_count") or 0) + sum(
        stored_finding_count_by_module.values()
    )
    summary_payload["latest_stored_evidence"] = [_stored_evidence_summary(item) for item in stored_evidence[:10]]
    return {"target_id": target_id, "operations_summary": summary_payload}


@router.get("/api/targets/{target_id}/m01/ai-context")
def get_target_m01_ai_context(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return a bounded M01 context pack for local LaIA/Mistral review."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    context_pack = build_m01_target_context_pack(_target_to_record(target))
    return {"context_pack": context_pack.to_dict()}


@router.get("/api/targets/{target_id}/m01/ai-prompt")
def get_target_m01_ai_prompt(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return a no-call prompt envelope and ChatML prompt for local Mistral."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    return {
        "prompt_envelope": build_m01_target_prompt_envelope(target_record),
        "chatml_prompt": render_m01_target_chatml_prompt(target_record),
    }


@router.post("/api/targets/{target_id}/m01/laia-review")
def run_target_m01_laia_review(
    target_id: str,
    payload: dict[str, Any],
    session: Session = Depends(get_session),
    client: MistralClient = Depends(get_target_mistral_client),
) -> dict[str, Any]:
    """Run a gated local Mistral review over persisted M01 target evidence."""
    if payload.get("execute_local_ai") is not True:
        raise HTTPException(status_code=400, detail="M01 LaIA review requires execute_local_ai=true.")
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    try:
        chatml_prompt = render_m01_target_chatml_prompt(target_record)
        review_text = client.generate_text(str(chatml_prompt["prompt"]))
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    review_path = write_m01_target_ai_review(
        target_record,
        model=client.model,
        prompt_sha256=str(chatml_prompt["prompt_sha256"]),
        content=review_text,
    )
    return {
        "mode": "m01_laia_mistral_local_review",
        "target_id": target_id,
        "model": client.model,
        "prompt_sha256": chatml_prompt["prompt_sha256"],
        "review_path": review_path.as_posix(),
        "content": review_text,
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
    }


@router.get("/api/targets/{target_id}/m01/laia-reviews")
def list_target_m01_laia_reviews(
    target_id: str, limit: int = Query(10, ge=1, le=50), session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Return persisted local LaIA/Mistral M01 reviews for a target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    reviews = list_m01_target_ai_reviews(_target_to_record(target), limit=limit)
    return {
        "target_id": target_id,
        "reviews": [review.to_dict() for review in reviews],
        "review_count": len(reviews),
    }


@router.get("/api/targets/{target_id}/m01/action-plan")
def get_target_m01_action_plan(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Build a current M01 operator plan from evidence and parsed local LaIA reviews."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    return {"action_plan": build_m01_action_plan(_target_to_record(target)).to_dict()}


@router.post("/api/targets/{target_id}/m01/action-plan/write")
def write_target_m01_action_plan(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Persist the current evidence-derived M01 operator plan for a target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    path = write_m01_action_plan(target_record)
    return {
        "target_id": target_id,
        "action_plan_path": path.as_posix(),
        "action_plan": build_m01_action_plan(target_record).to_dict(),
    }


@router.get("/api/targets/{target_id}/m01/action-board")
def get_target_m01_action_board(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return the M01 plan merged with persisted operator-only progress."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    return {"action_board": build_m01_action_board(_target_to_record(target))}


@router.get("/api/targets/{target_id}/modules/{module_id}/ai-context")
def get_target_module_ai_context(
    target_id: str, module_id: str, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Build bounded LaIA context from actual saved artifacts for an official non-M01 module."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    store = EvidenceStore(session)
    stored_findings, stored_evidence_count, stored_unverified_count = _stored_module_findings(store, target_id, module_id)
    try:
        pack = build_target_module_context_pack(
            target_record,
            module_id,
            extra_findings=stored_findings,
            source_stored_evidence_count=stored_evidence_count,
            unverified_stored_evidence_count=stored_unverified_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"context_pack": pack}


@router.get("/api/targets/{target_id}/modules/{module_id}/ai-prompt")
def get_target_module_ai_prompt(
    target_id: str, module_id: str, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Return a no-call local LaIA/Mistral prompt for an official module workspace."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    store = EvidenceStore(session)
    stored_findings, stored_evidence_count, stored_unverified_count = _stored_module_findings(store, target_id, module_id)
    try:
        prompt = render_target_module_chatml_prompt(
            target_record,
            module_id,
            extra_findings=stored_findings,
            source_stored_evidence_count=stored_evidence_count,
            unverified_stored_evidence_count=stored_unverified_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"chatml_prompt": prompt}


@router.post("/api/targets/{target_id}/modules/{module_id}/laia-review")
def run_target_module_laia_review(
    target_id: str,
    module_id: str,
    payload: dict[str, Any],
    session: Session = Depends(get_session),
    client: MistralClient = Depends(get_target_mistral_client),
) -> dict[str, Any]:
    """Execute an explicitly confirmed local review and persist its module-scoped receipt."""
    if payload.get("execute_local_ai") is not True:
        raise HTTPException(status_code=400, detail="Module LaIA review requires execute_local_ai=true.")
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    try:
        prompt = render_target_module_chatml_prompt(target_record, module_id)
        content = client.generate_text(str(prompt["prompt"]))
        review_path = write_target_module_ai_review(
            target_record, module_id, client.model, str(prompt["prompt_sha256"]), content
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "target_id": target_id,
        "module_id": module_id,
        "model": client.model,
        "prompt_sha256": prompt["prompt_sha256"],
        "review_path": review_path.as_posix(),
        "content": content,
        "external_ai_call_performed": False,
        "local_ai_call_performed": True,
    }


@router.get("/api/targets/{target_id}/modules/{module_id}/laia-reviews")
def get_target_module_laia_reviews(
    target_id: str,
    module_id: str,
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Return persisted local LaIA/Mistral receipts for one official target module."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        reviews = list_target_module_ai_reviews(_target_to_record(target), module_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"target_id": target_id, "module_id": module_id, "reviews": list(reviews), "review_count": len(reviews)}


@router.get("/api/targets/{target_id}/modules/{module_id}/action-plan")
def get_target_module_action_plan(
    target_id: str, module_id: str, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Build a current operator action plan from persisted target-module findings."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    store = EvidenceStore(session)
    stored_findings, stored_evidence_count, stored_unverified_count = _stored_module_findings(store, target_id, module_id)
    try:
        plan = build_module_action_plan(
            target_record,
            module_id,
            extra_findings=stored_findings,
            source_stored_evidence_count=stored_evidence_count,
            unverified_stored_evidence_count=stored_unverified_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"target_id": target_id, "module_id": module_id, "action_plan": plan.to_dict()}


@router.post("/api/targets/{target_id}/modules/{module_id}/action-plan/write")
def write_target_module_action_plan(
    target_id: str, module_id: str, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist the current evidence-derived operator action plan for one target module."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    store = EvidenceStore(session)
    stored_findings, stored_evidence_count, stored_unverified_count = _stored_module_findings(store, target_id, module_id)
    try:
        path = write_module_action_plan(
            target_record,
            module_id,
            extra_findings=stored_findings,
            source_stored_evidence_count=stored_evidence_count,
            unverified_stored_evidence_count=stored_unverified_count,
        )
        plan = build_module_action_plan(
            target_record,
            module_id,
            extra_findings=stored_findings,
            source_stored_evidence_count=stored_evidence_count,
            unverified_stored_evidence_count=stored_unverified_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "target_id": target_id,
        "module_id": plan.module_id,
        "action_plan_path": path.as_posix(),
        "action_plan": plan.to_dict(),
    }


@router.get("/api/targets/{target_id}/modules/{module_id}/action-board")
def get_target_module_action_board(
    target_id: str, module_id: str, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Return the module plan merged with persisted operator-only progress."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    store = EvidenceStore(session)
    stored_findings, stored_evidence_count, stored_unverified_count = _stored_module_findings(store, target_id, module_id)
    try:
        board = build_module_action_board(
            target_record,
            module_id,
            extra_findings=stored_findings,
            source_stored_evidence_count=stored_evidence_count,
            unverified_stored_evidence_count=stored_unverified_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"target_id": target_id, "module_id": module_id, "action_board": board}


@router.post("/api/targets/{target_id}/modules/{module_id}/action-board/progress")
def update_target_module_action_board_progress(
    target_id: str,
    module_id: str,
    payload: ModuleActionProgressRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Persist an operator-confirmed progress event for a module action step."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    store = EvidenceStore(session)
    stored_findings, stored_evidence_count, stored_unverified_count = _stored_module_findings(store, target_id, module_id)
    try:
        board = update_module_action_progress(
            target_record,
            module_id,
            step_id=payload.step_id,
            status=payload.status,
            note=payload.note,
            extra_findings=stored_findings,
            source_stored_evidence_count=stored_evidence_count,
            unverified_stored_evidence_count=stored_unverified_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"target_id": target_id, "module_id": module_id, "action_board": board}


@router.post("/api/targets/{target_id}/m02/service-inventory")
def write_target_m02_service_inventory(
    target_id: str, payload: M02ServiceInventoryRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist approved service/version observations and optional public NVD candidate data for M02."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        observations = [service_observation_from_payload(item) for item in payload.services]
        path = write_m02_service_inventory(_target_to_record(target), observations, fetch_external=payload.fetch_external)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    inventory = read_m02_service_inventory(_target_to_record(target))
    return {
        "target_id": target_id,
        "inventory_path": path.as_posix(),
        "inventory": inventory,
        "module_run": _module_run_payload(target, "m02_vulnerabilities", "service_inventory", path.as_posix(), inventory),
        "module_findings": _module_findings_payload("m02_vulnerabilities", inventory),
    }


@router.get("/api/targets/{target_id}/m02/service-inventory")
def get_target_m02_service_inventory(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return the persisted M02 service inventory without running a scan or external lookup."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    inventory = read_m02_service_inventory(_target_to_record(target))
    return {"target_id": target_id, "inventory": inventory, "inventory_found": inventory is not None}


@router.post("/api/targets/{target_id}/m03/service-map")
def write_target_m03_service_map(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Build and persist M03 service classification from saved M02 evidence only."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    path = write_m03_service_map(target_record)
    service_map = read_m03_service_map(target_record)
    return {
        "target_id": target_id,
        "service_map_path": path.as_posix(),
        "service_map": service_map,
        "module_run": _module_run_payload(target, "m03_network_services", "service_map", path.as_posix(), service_map),
        "module_findings": _module_findings_payload("m03_network_services", service_map),
    }


@router.get("/api/targets/{target_id}/m03/service-map")
def get_target_m03_service_map(target_id: str, refresh: bool = False, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Read a persisted M03 map or build an in-memory map from saved M02 evidence when requested."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    service_map = build_m03_service_map(target_record) if refresh else read_m03_service_map(target_record)
    return {"target_id": target_id, "service_map": service_map, "service_map_found": service_map is not None}


@router.post("/api/targets/{target_id}/m04/web-baseline")
def write_target_m04_web_baseline(
    target_id: str, payload: M04WebBaselineRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist operator-observed HTTP metadata and deterministic M04 header posture; no request is made."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        observation = web_response_observation_from_payload(payload.model_dump())
        path = write_m04_web_baseline(_target_to_record(target), observation)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    baseline = read_m04_web_baseline(_target_to_record(target))
    return {
        "target_id": target_id,
        "baseline_path": path.as_posix(),
        "baseline": baseline,
        "module_run": _module_run_payload(target, "m04_web_intrusion", "web_baseline", path.as_posix(), baseline),
        "module_findings": _module_findings_payload("m04_web_intrusion", baseline),
    }


@router.get("/api/targets/{target_id}/m04/web-baseline")
def get_target_m04_web_baseline(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return stored M04 web baseline without contacting the URL."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    baseline = read_m04_web_baseline(_target_to_record(target))
    return {"target_id": target_id, "baseline": baseline, "baseline_found": baseline is not None}


@router.post("/api/targets/{target_id}/m05/credential-evidence")
def write_target_m05_credential_evidence(
    target_id: str, payload: M05CredentialEvidenceRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Fingerprint transient credential material and persist only secret-free M05 evidence."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        evidence = credential_evidence_from_payload(payload.model_dump())
        path = write_m05_credential_evidence(_target_to_record(target), evidence)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "target_id": target_id,
        "receipt_path": path.as_posix(),
        "secret_material_persisted": False,
        "module_run": _module_run_payload(
            target,
            "m05_credentials",
            "credential_evidence",
            path.as_posix(),
            flags={"secret_material_persisted": False},
        ),
        "module_findings": _module_findings_payload("m05_credentials", None, path.as_posix()),
    }


@router.get("/api/targets/{target_id}/m05/credential-evidence")
def get_target_m05_credential_evidence(
    target_id: str, limit: int = Query(100, ge=1, le=100), session: Session = Depends(get_session)
) -> dict[str, Any]:
    """List secret-free M05 credential receipts for the target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    receipts = list_m05_credential_evidence(_target_to_record(target), limit=limit)
    return {"target_id": target_id, "receipts": list(receipts), "receipt_count": len(receipts), "secret_material_persisted": False}


@router.post("/api/targets/{target_id}/m05/credential-evidence/{receipt_id}/verify")
def verify_target_m05_credential_evidence(
    target_id: str,
    receipt_id: str,
    payload: M05CredentialVerificationRequest,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Verify local material against saved evidence without remote authentication or secret persistence."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        return verify_m05_credential_material(_target_to_record(target), receipt_id, payload.secret_material)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/targets/{target_id}/m06/packet-capture")
async def ingest_target_m06_packet_capture(
    target_id: str,
    capture: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Store and inspect a supplied packet-capture file; this endpoint never starts capture activity."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        receipt = write_m06_capture_evidence(
            _target_to_record(target), capture.file, capture.filename or "capture.bin", capture.content_type
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await capture.close()
    return {
        **receipt,
        "module_run": _module_run_payload(
            target,
            "m06_mitm_network",
            "packet_capture_intake",
            str(receipt["receipt_path"]),
            dict(receipt),
            flags={"target_activity_performed": False},
        ),
        "module_findings": _module_findings_payload("m06_mitm_network", dict(receipt)),
    }


@router.get("/api/targets/{target_id}/m06/packet-captures")
def get_target_m06_packet_captures(
    target_id: str, limit: int = Query(100, ge=1, le=100), session: Session = Depends(get_session)
) -> dict[str, Any]:
    """List packet-capture evidence receipts without reading capture packet contents."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    captures = list_m06_capture_evidence(_target_to_record(target), limit=limit)
    return {"target_id": target_id, "captures": list(captures), "capture_count": len(captures)}


@router.post("/api/targets/{target_id}/m07/session-evidence")
def write_target_m07_session_evidence(
    target_id: str, payload: M07SessionEvidenceRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist metadata for an existing authorized session without commands or session secrets."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        evidence = session_evidence_from_payload(payload.model_dump())
        path = write_m07_session_evidence(_target_to_record(target), evidence)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "target_id": target_id,
        "receipt_path": path.as_posix(),
        "command_execution_performed": False,
        "module_run": _module_run_payload(
            target,
            "m07_post_exploitation",
            "session_evidence",
            path.as_posix(),
            flags={"command_execution_performed": False},
        ),
        "module_findings": _module_findings_payload("m07_post_exploitation", None, path.as_posix()),
    }


@router.get("/api/targets/{target_id}/m07/session-evidence")
def get_target_m07_session_evidence(
    target_id: str, limit: int = Query(100, ge=1, le=100), session: Session = Depends(get_session)
) -> dict[str, Any]:
    """List secret-free M07 session evidence without touching a remote host."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    sessions = list_m07_session_evidence(_target_to_record(target), limit=limit)
    return {"target_id": target_id, "sessions": list(sessions), "session_count": len(sessions), "network_activity_performed": False}


@router.post("/api/targets/{target_id}/m08/resilience-measurements")
def write_target_m08_resilience_measurements(
    target_id: str, payload: M08ResilienceMeasurementsRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist supplied monitoring data and calculate its sample-only resilience summary."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        measurements = [measurement_from_payload(item) for item in payload.measurements]
        path = write_m08_resilience_measurements(_target_to_record(target), measurements)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    report = read_m08_resilience_measurements(_target_to_record(target))
    return {
        "target_id": target_id,
        "measurements_path": path.as_posix(),
        "report": report,
        "module_run": _module_run_payload(target, "m08_dos_resilience", "resilience_measurements", path.as_posix(), report),
        "module_findings": _module_findings_payload("m08_dos_resilience", report),
    }


@router.get("/api/targets/{target_id}/m08/resilience-measurements")
def get_target_m08_resilience_measurements(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Read the persisted M08 measurement report without generating any traffic."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    report = read_m08_resilience_measurements(_target_to_record(target))
    return {"target_id": target_id, "report": report, "report_found": report is not None, "load_generated_by_application": False}


@router.post("/api/targets/{target_id}/m09/intelligence-dataset")
def write_target_m09_intelligence_dataset(
    target_id: str, payload: M09IntelligenceDatasetRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Normalize and persist already collected records for M09 without fetching source URLs."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        records = [normalize_intelligence_record(item) for item in payload.records]
        path = write_m09_intelligence_dataset(_target_to_record(target), records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    dataset = read_m09_intelligence_dataset(_target_to_record(target))
    return {
        "target_id": target_id,
        "dataset_path": path.as_posix(),
        "dataset": dataset,
        "module_run": _module_run_payload(target, "m09_scraping_intelligence", "intelligence_dataset", path.as_posix(), dataset),
        "module_findings": _module_findings_payload("m09_scraping_intelligence", dataset),
    }


@router.get("/api/targets/{target_id}/m09/intelligence-dataset")
def get_target_m09_intelligence_dataset(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Read M09 normalized records without requesting or crawling source URLs."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    dataset = read_m09_intelligence_dataset(_target_to_record(target))
    return {"target_id": target_id, "dataset": dataset, "dataset_found": dataset is not None, "connector_execution_performed": False}


@router.post("/api/targets/{target_id}/m10/radio-observations")
def write_target_m10_radio_observations(
    target_id: str, payload: M10RadioObservationsRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist passive radio observations only; RF hardware is never activated."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        observations = [radio_observation_from_payload(item) for item in payload.observations]
        path = write_m10_radio_observations(_target_to_record(target), observations)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    report = read_m10_radio_observations(_target_to_record(target))
    return {
        "target_id": target_id,
        "observations_path": path.as_posix(),
        "report": report,
        "module_run": _module_run_payload(target, "m10_wireless_rf", "radio_observations", path.as_posix(), report),
        "module_findings": _module_findings_payload("m10_wireless_rf", report),
    }


@router.get("/api/targets/{target_id}/m10/radio-observations")
def get_target_m10_radio_observations(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Read stored passive M10 observations without RF capture or transmission."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    report = read_m10_radio_observations(_target_to_record(target))
    return {"target_id": target_id, "report": report, "report_found": report is not None, "rf_transmission_performed": False}


@router.post("/api/targets/{target_id}/m11/device-inventory")
def write_target_m11_device_inventory(
    target_id: str, payload: M11DeviceInventoryRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist physical-device observations without pairing, querying or controlling devices."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        observations = [device_observation_from_payload(item) for item in payload.observations]
        path = write_m11_device_inventory(_target_to_record(target), observations)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    inventory = read_m11_device_inventory(_target_to_record(target))
    return {
        "target_id": target_id,
        "inventory_path": path.as_posix(),
        "inventory": inventory,
        "module_run": _module_run_payload(target, "m11_iot_physical", "device_inventory", path.as_posix(), inventory),
        "module_findings": _module_findings_payload("m11_iot_physical", inventory),
    }


@router.get("/api/targets/{target_id}/m11/device-inventory")
def get_target_m11_device_inventory(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Read the stored M11 inventory without interacting with a physical device."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    inventory = read_m11_device_inventory(_target_to_record(target))
    return {"target_id": target_id, "inventory": inventory, "inventory_found": inventory is not None, "device_interaction_performed": False}


@router.post("/api/targets/{target_id}/m12/evidence-ledger")
def write_target_m12_evidence_ledger(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Index saved evidence from prior target modules and persist an M12 integrity ledger."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    evidence_store = EvidenceStore(session)
    stored_evidence = _stored_evidence_to_payloads(
        evidence_store.list_target(target_id, limit=500),
        evidence_store,
        verify_content=True,
    )
    path = write_m12_evidence_ledger(target_record, stored_evidence=stored_evidence)
    ledger = read_m12_evidence_ledger(target_record)
    return {
        "target_id": target_id,
        "ledger_path": path.as_posix(),
        "ledger": ledger,
        "module_run": _module_run_payload(target, "m12_orchestration", "evidence_ledger", path.as_posix(), ledger),
        "module_findings": _module_findings_payload("m12_orchestration", ledger),
    }


@router.get("/api/targets/{target_id}/m12/evidence-ledger")
def get_target_m12_evidence_ledger(
    target_id: str, refresh: bool = False, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Read the M12 evidence ledger or build an in-memory index of persisted artifacts only."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    if refresh:
        evidence_store = EvidenceStore(session)
        stored_evidence = _stored_evidence_to_payloads(
            evidence_store.list_target(target_id, limit=500),
            evidence_store,
            verify_content=True,
        )
        ledger = build_m12_evidence_ledger(target_record, stored_evidence=stored_evidence)
    else:
        ledger = read_m12_evidence_ledger(target_record)
    return {"target_id": target_id, "ledger": ledger, "ledger_found": ledger is not None, "target_activity_performed": False}


@router.post("/api/targets/{target_id}/m13/apk")
async def write_target_m13_apk_evidence(
    target_id: str, apk: UploadFile = File(...), session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Ingest and structurally inspect an uploaded Android APK in the target workspace."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        receipt = write_m13_apk_evidence(
            _target_to_record(target), apk.file, apk.filename or "application.apk", apk.content_type
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        await apk.close()
    return {
        "target_id": target_id,
        "apk": receipt,
        "module_run": _module_run_payload(
            target,
            "m13_android",
            "apk_evidence",
            str(receipt["receipt_path"]),
            dict(receipt),
            flags={"device_interaction_performed": False},
        ),
        "module_findings": _module_findings_payload("m13_android", dict(receipt)),
    }


@router.get("/api/targets/{target_id}/m13/apks")
def get_target_m13_apk_evidence(
    target_id: str, limit: int = Query(default=100, ge=1, le=500), session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Return saved APK structural inspection receipts for this target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        receipts = list_m13_apk_evidence(_target_to_record(target), limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"target_id": target_id, "apks": list(receipts), "apk_count": len(receipts)}


@router.post("/api/targets/{target_id}/m14/awareness-campaigns")
def write_target_m14_awareness_campaign(
    target_id: str, payload: M14AwarenessCampaignRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist an M14 awareness campaign definition and hashed recipient roster."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        campaign = awareness_campaign_from_payload(payload.model_dump())
        path = write_m14_awareness_campaign(_target_to_record(target), campaign)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    campaigns = list(read_m14_awareness_campaigns(_target_to_record(target)))
    return {
        "target_id": target_id,
        "campaign_path": path.as_posix(),
        "campaigns": campaigns,
        "module_run": _module_run_payload(target, "m14_phishing", "awareness_campaign", path.as_posix(), campaigns[0] if campaigns else None),
        "module_findings": _module_findings_payload("m14_phishing", campaigns[0] if campaigns else None),
    }


@router.post("/api/targets/{target_id}/m14/awareness-campaigns/{campaign_id}/outcomes")
def write_target_m14_awareness_outcomes(
    target_id: str, campaign_id: str, payload: M14AwarenessOutcomesRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Attach imported campaign outcome observations to a stored M14 campaign."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        path = write_m14_awareness_outcomes(_target_to_record(target), campaign_id, payload.outcomes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    campaigns = list(read_m14_awareness_campaigns(_target_to_record(target)))
    return {
        "target_id": target_id,
        "campaign_path": path.as_posix(),
        "campaigns": campaigns,
        "module_run": _module_run_payload(target, "m14_phishing", "awareness_outcomes", path.as_posix(), campaigns[0] if campaigns else None),
        "module_findings": _module_findings_payload("m14_phishing", campaigns[0] if campaigns else None),
    }


@router.get("/api/targets/{target_id}/m14/awareness-campaigns")
def get_target_m14_awareness_campaigns(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """List M14 awareness campaigns and their imported outcome summaries."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    campaigns = read_m14_awareness_campaigns(_target_to_record(target))
    return {"target_id": target_id, "campaigns": list(campaigns), "campaign_count": len(campaigns)}


@router.post("/api/targets/{target_id}/m15/cloud-inventory")
def write_target_m15_cloud_inventory(
    target_id: str, payload: M15CloudInventoryRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist a supplied cloud, container, or Kubernetes inventory export."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        assets = [cloud_asset_from_payload(item) for item in payload.assets]
        path = write_m15_cloud_inventory(_target_to_record(target), assets)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    inventory = read_m15_cloud_inventory(_target_to_record(target))
    return {
        "target_id": target_id,
        "inventory_path": path.as_posix(),
        "inventory": inventory,
        "module_run": _module_run_payload(target, "m15_cloud", "cloud_inventory", path.as_posix(), inventory),
        "module_findings": _module_findings_payload("m15_cloud", inventory),
    }


@router.get("/api/targets/{target_id}/m15/cloud-inventory")
def get_target_m15_cloud_inventory(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Read the current target M15 cloud inventory."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    inventory = read_m15_cloud_inventory(_target_to_record(target))
    return {"target_id": target_id, "inventory": inventory, "inventory_found": inventory is not None}


@router.post("/api/targets/{target_id}/m01/action-board/progress")
def update_target_m01_action_board_progress(
    target_id: str, payload: M01ActionProgressRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    """Persist an auditable operator progress event for an active M01 plan step."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    try:
        board = update_m01_action_progress(
            _target_to_record(target), step_id=payload.step_id, status=payload.status, note=payload.note
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"action_board": board}


@router.get("/api/targets/{target_id}")
def get_target(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return a target and its latest fingerprint."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    return {
        "target": _target_to_payload(target),
        "fingerprint": _fingerprint_to_payload(repository.get_latest_fingerprint(target_id)),
    }


@router.get("/api/targets")
def list_targets(limit: int = 50, session: Session = Depends(get_session)) -> dict[str, Any]:
    """List recent targets."""
    repository = TargetsRepository(session)
    return {"targets": [_target_to_payload(target) for target in repository.list_targets(limit=limit)]}


@router.post("/api/targets/{target_id}/plan")
def plan_target(
    target_id: str,
    confirmed: bool = False,
    allowlisted_target: bool = True,
    hardware_available: bool = True,
    network_available: bool = True,
    user_logic_available: bool = False,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Build a real non-executing X5/OjoRouter plan for a stored target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    router, registry_snapshot = _runtime_router()
    plan = router.plan_target(
        _target_to_record(target),
        confirmed=confirmed,
        allowlisted_target=allowlisted_target,
        hardware_available=hardware_available,
        network_available=network_available,
        user_logic_available=user_logic_available,
    )
    return {
        "target": _target_to_payload(target),
        "fingerprint": _fingerprint_to_payload(repository.get_latest_fingerprint(target_id)),
        "registered_technique_ids": router.list_registered_technique_ids(),
        "runtime_registry": _runtime_registry_payload(registry_snapshot),
        "execution_started": False,
        "plan": _plan_to_payload(plan),
    }


@router.post("/api/targets/{target_id}/fingerprint/refresh")
def refresh_target_fingerprint(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Persist and return a fresh deterministic local fingerprint for a target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    fingerprint = repository.refresh_fingerprint(target)
    return {
        "target": _target_to_payload(target),
        "fingerprint": _fingerprint_to_payload(fingerprint),
    }


@router.get("/api/targets/{target_id}/context")
def get_target_context(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return target context ready for UI and AI-assisted planning surfaces."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    router, registry_snapshot = _runtime_router()
    plan = router.plan_target(_target_to_record(target))
    return {
        "target": _target_to_payload(target),
        "fingerprint": _fingerprint_to_payload(repository.get_latest_fingerprint(target_id)),
        "planning": _plan_to_payload(plan),
        "execution_started": False,
        "runtime": {
            "registered_technique_count": len(router.list_registered_technique_ids()),
            "registry_ready": registry_snapshot.ready,
            "registry_packages": [package.to_dict() for package in registry_snapshot.packages],
            "job_runner_required_for_start": True,
        },
    }


@router.get("/api/targets/{target_id}/attack-surface")
def get_target_attack_surface(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return a passive attack-surface graph derived from stored target facts."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    stored_fingerprint = repository.get_latest_fingerprint(target_id)
    if stored_fingerprint is None:
        fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)
    else:
        fingerprint = _fingerprint_model_to_contract(stored_fingerprint)
    graph = build_attack_surface_graph(target_record, fingerprint)
    return {
        "target": _target_to_payload(target),
        "fingerprint": _fingerprint_to_payload(stored_fingerprint),
        "graph": graph.to_dict(),
        "execution_started": False,
    }


@router.get("/api/targets/{target_id}/services")
def get_target_services(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return passive service fingerprints derived from target facts and metadata."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    stored_fingerprint = repository.get_latest_fingerprint(target_id)
    if stored_fingerprint is None:
        fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)
    else:
        fingerprint = _fingerprint_model_to_contract(stored_fingerprint)
    try:
        report = build_service_fingerprint_report(target_record, fingerprint)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "target": _target_to_payload(target),
        "fingerprint": _fingerprint_to_payload(stored_fingerprint),
        "services": report.to_dict(),
    }


@router.get("/api/targets/{target_id}/workspace")
def get_target_workspace(target_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Inspect the target workspace binding without creating files."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    return {
        "target": _target_to_payload(target),
        "workspace": collect_target_workspace_state(target_record).to_dict(),
    }


@router.post("/api/targets/{target_id}/workspace")
def ensure_target_workspace_route(
    target_id: str,
    payload: TargetWorkspaceBindRequest | None = None,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """Create a target workspace and optional per-target module bindings."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    request = payload or TargetWorkspaceBindRequest()
    workspace = ensure_target_workspace(target_record)
    bindings = []
    try:
        for module_id in _select_workspace_module_ids(target_record, request):
            bindings.append(bind_target_module_workspace(target_record, module_id).to_dict())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "target": _target_to_payload(target),
        "workspace": workspace.to_dict(),
        "workspace_state": collect_target_workspace_state(target_record).to_dict(),
        "bindings": bindings,
    }


def run_target_job_start(
    target_id: str,
    request_payload: TargetJobStartRequest,
    session: Session,
) -> Any:
    """Create, run, persist and return one target job from a validated operator selection."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    target_record = _target_to_record(target)
    router, registry_snapshot = _runtime_router()
    plan = router.plan_target(
        target_record,
        confirmed=request_payload.confirmed,
        allowlisted_target=request_payload.allowlisted_target,
        hardware_available=request_payload.hardware_available,
        network_available=request_payload.network_available,
        user_logic_available=request_payload.user_logic_available,
    )
    selected_techniques = _selected_techniques_from_payload_or_plan(request_payload, plan)
    runnable_technique_ids = {step.technique_id for step in plan.runnable_steps}
    if not selected_techniques:
        return _start_blocked_response(target, plan, "X5 found no runnable techniques for this target and payload.")
    blocked_selection = [technique_id for technique_id in selected_techniques if technique_id not in runnable_technique_ids]
    if blocked_selection:
        return _start_blocked_response(
            target,
            plan,
            "Selected techniques are not runnable now: " + ", ".join(blocked_selection),
        )
    jobs_repository = JobsRepository(session)
    job = jobs_repository.create_queued_job(
        target_id=target_id,
        created_by=request_payload.created_by,
        mode=request_payload.mode,
        selected_modules=request_payload.selected_modules or target_record.allowed_modules,
        selected_techniques=selected_techniques,
        permissions_snapshot={"parameters": request_payload.parameters},
    )
    runner_request = jobs_repository.to_job_request(
        job,
        permissions_snapshot={
            "parameters": request_payload.parameters,
            "confirmed": request_payload.confirmed,
        },
    )
    try:
        jobs_repository.mark_running(job)
        evidence_store = EvidenceStore(session)
        result = JobRunner(registry_snapshot.registry, evidence_store=evidence_store).run_job(runner_request)
    except ContractError as exc:
        result = JobResult(
            job_id=job.job_id,
            status=JOB_STATUS_FAILED,
            result_status=RESULT_FAILED,
            summary="Job failed contract validation.",
            error=str(exc),
        )
    completed_job = jobs_repository.complete_job(job, result)
    stored_evidence = [_stored_evidence_to_payload(stored) for stored in EvidenceStore(session).list_run(job.job_id)]
    return {
        "target": _target_to_payload(target),
        "job": _job_to_payload(completed_job),
        "stored_evidence": stored_evidence,
        "stored_evidence_count": len(stored_evidence),
        "plan": _plan_to_payload(plan),
        "runtime_registry": _runtime_registry_payload(registry_snapshot),
        "execution_started": True,
    }


@router.post("/api/targets/{target_id}/start")
def start_target(
    target_id: str,
    payload: TargetJobStartRequest | None = None,
    session: Session = Depends(get_session),
) -> Any:
    """Create, run and persist a target job through the local in-process JobRunner."""
    if payload is None:
        return _not_available(
            "Starting a target requires an explicit job request payload with operator-selected mode and confirmation flags."
        )
    return run_target_job_start(target_id, payload, session)


@router.get("/api/targets/{target_id}/jobs")
def list_target_jobs(target_id: str, limit: int = 50, session: Session = Depends(get_session)) -> dict[str, Any]:
    """List persisted jobs for a target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    jobs = JobsRepository(session).list_for_target(target_id, limit=limit)
    return {
        "target": _target_to_payload(target),
        "jobs": [_job_to_payload(job) for job in jobs],
        "count": len(jobs),
    }


@router.get("/api/targets/{target_id}/evidence")
def list_target_evidence(
    target_id: str,
    limit: int = 100,
    verify_content: bool = Query(False),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """List persisted EvidenceStore metadata for a target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    store = EvidenceStore(session)
    evidence = store.list_target(target_id, limit=limit)
    return {
        "target": _target_to_payload(target),
        "evidence": _stored_evidence_to_payloads(evidence, store, verify_content=verify_content),
        "count": len(evidence),
        "content_verification_performed": verify_content,
    }


@router.get("/api/targets/{target_id}/modules/{module_id}/evidence")
def list_target_module_evidence(
    target_id: str,
    module_id: str,
    limit: int = 100,
    verify_content: bool = Query(False),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """List persisted EvidenceStore metadata for one target-scoped module."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    store = EvidenceStore(session)
    evidence = store.list_target_module(target_id, module_id, limit=limit)
    return {
        "target": _target_to_payload(target),
        "module_id": module_id,
        "evidence": _stored_evidence_to_payloads(evidence, store, verify_content=verify_content),
        "count": len(evidence),
        "content_verification_performed": verify_content,
    }


@router.get("/api/targets/{target_id}/jobs/{job_id}/evidence")
def list_target_job_evidence(
    target_id: str,
    job_id: str,
    limit: int = 100,
    verify_content: bool = Query(False),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    """List persisted EvidenceStore metadata for one target job."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    job = JobsRepository(session).get_by_job_id(job_id)
    if job is None or job.target_id != target_id:
        raise HTTPException(status_code=404, detail="Job not found for target.")
    store = EvidenceStore(session)
    evidence = store.list_run(job_id, limit=limit)
    return {
        "target": _target_to_payload(target),
        "job": _job_to_payload(job),
        "evidence": _stored_evidence_to_payloads(evidence, store, verify_content=verify_content),
        "count": len(evidence),
        "content_verification_performed": verify_content,
    }


@router.get("/api/targets/{target_id}/evidence/{evidence_id}")
def get_target_evidence_content(target_id: str, evidence_id: str, session: Session = Depends(get_session)) -> dict[str, Any]:
    """Return persisted EvidenceStore metadata and JSON content for one target evidence id."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    store = EvidenceStore(session)
    stored = store.get_record(evidence_id)
    if stored is None or stored.target_id != target_id:
        raise HTTPException(status_code=404, detail="Evidence not found for target.")
    content_result = store.read_content_result(evidence_id)
    return {
        "target": _target_to_payload(target),
        "evidence": _stored_evidence_to_payload(stored),
        "content": content_result.content,
        "content_hash_verified": content_result.verified,
        "content_read_status": "verified" if content_result.verified else "unverified",
        "content_read_error": content_result.failure_reason,
    }


@router.post("/api/targets/{target_id}/stop")
def stop_target(target_id: str, session: Session = Depends(get_session)) -> Any:
    """Request cooperative stop for active queued/running jobs of a target."""
    repository = TargetsRepository(session)
    target = _require_target(repository, target_id)
    jobs_repository = JobsRepository(session)
    active_jobs = jobs_repository.request_stop_for_target(target_id)
    stop_requests = [
        write_job_stop_request(job.job_id, target_id, reason="operator_requested_target_stop").to_dict()
        for job in active_jobs
    ]
    if not active_jobs:
        recent_jobs = jobs_repository.list_for_target(target_id, limit=1)
        return JSONResponse(
            status_code=501,
            content={
                "status": "not_available_yet",
                "stop_state": "no_active_jobs",
                "reason": "No queued or running jobs exist for this target.",
                "target": _target_to_payload(target),
                "stop_requested": False,
                "active_job_count": 0,
                "latest_job": _job_to_payload(recent_jobs[0]) if recent_jobs else None,
            },
        )
    return {
        "status": "stop_requested",
        "target": _target_to_payload(target),
        "stop_requested": True,
        "active_job_count": len(active_jobs),
        "jobs": [_job_to_payload(job) for job in active_jobs],
        "stop_requests": stop_requests,
    }
