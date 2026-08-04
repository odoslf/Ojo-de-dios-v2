"""HTML pages for target creation and target detail."""

import json
from typing import Any

from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.ai.mistral_client import MistralClient
from app.config import get_settings
from app.core.errors import ConfigurationError, ContractError
from app.core.module_catalog import list_modules
from app.core.ojo_router import OjoRouter
from app.core.runtime_registry import get_runtime_registry_snapshot
from app.core.target_fingerprint import build_target_fingerprint
from app.ai.m01_context import (
    list_m01_target_ai_reviews,
    render_m01_target_chatml_prompt,
    write_m01_target_ai_review,
)
from app.core.m01_action_plan import build_m01_action_plan, write_m01_action_plan
from app.core.m01_action_tracking import build_m01_action_board, update_m01_action_progress
from app.core.target_osint import list_target_passive_dns_history, run_target_passive_dns
from app.core.target_model import (
    TARGET_MODE_DRY_RUN,
    TargetRecord,
    TargetRequest,
    VALID_TARGET_MODES,
    VALID_TARGET_TYPES,
)
from app.api.routes_targets import TargetJobStartRequest, run_target_job_start
from app.db.repositories.targets_repository import TargetsRepository
from app.db.session import get_session

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _target_mistral_client() -> MistralClient:
    settings = get_settings()
    return MistralClient(
        base_url=settings.ollama_base_url,
        model=settings.mistral_model,
        timeout_seconds=settings.mistral_timeout_seconds,
        enabled=settings.ai_enabled and settings.mistral_enabled,
    )


def _target_detail_context(
    request: Request,
    target: Any,
    fingerprint: Any | None,
    plan: Any,
    runtime_registry: Any,
    target_record: TargetRecord,
    m01_passive_dns_result: dict[str, Any] | None = None,
    m01_passive_dns_error: str | None = None,
    m01_laia_review_error: str | None = None,
    m01_laia_review_success: str | None = None,
    m01_action_plan_success: str | None = None,
    m01_action_progress_error: str | None = None,
    m01_action_progress_success: str | None = None,
    product_flow_result: dict[str, Any] | None = None,
    product_flow_error: str | None = None,
) -> dict[str, Any]:
    return {
        "request": request,
        "target": target,
        "fingerprint": _fingerprint_payload(fingerprint),
        "plan": plan,
        "runtime_registry": runtime_registry.to_status_payload(),
        "m01_passive_dns_result": m01_passive_dns_result,
        "m01_passive_dns_error": m01_passive_dns_error,
        "m01_passive_dns_history": [entry.to_dict() for entry in list_target_passive_dns_history(target_record)],
        "m01_laia_reviews": [review.to_dict() for review in list_m01_target_ai_reviews(target_record)],
        "m01_laia_review_error": m01_laia_review_error,
        "m01_laia_review_success": m01_laia_review_success,
        "m01_action_plan": build_m01_action_plan(target_record).to_dict(),
        "m01_action_plan_success": m01_action_plan_success,
        "m01_action_board": build_m01_action_board(target_record),
        "m01_action_progress_error": m01_action_progress_error,
        "m01_action_progress_success": m01_action_progress_success,
        "product_flow_result": product_flow_result,
        "product_flow_error": product_flow_error,
    }


def _parse_allowed_modules(value: str) -> list[str]:
    """Parse comma/newline-separated module ids from the HTML form."""
    normalized = value.replace("\n", ",")
    return [module_id.strip() for module_id in normalized.split(",") if module_id.strip()]


def _selectable_runtime_modules() -> list[dict[str, Any]]:
    """Return catalog modules that currently expose runtime techniques."""
    runtime_modules = {technique_cls().module_id for technique_cls in get_runtime_registry_snapshot().registry.list_all()}
    return [module.to_dict() for module in list_modules(include_reserved=True) if module.module_id in runtime_modules]


def _create_target_from_form(
    repository: TargetsRepository,
    name: str,
    target_type: str,
    value: str,
    mode: str,
    allowed_modules: str,
    noise_profile: str,
    evidence_profile: str,
    require_confirmations: bool,
):
    """Create a target and its initial fingerprint from validated form fields."""
    request = TargetRequest(
        name=name,
        target_type=target_type,
        value=value,
        mode=mode,
        allowed_modules=_parse_allowed_modules(allowed_modules),
        noise_profile=noise_profile,
        evidence_profile=evidence_profile,
        require_confirmations=require_confirmations,
    )
    target = repository.create_target(request)
    fingerprint = build_target_fingerprint(target.target_id, target.target_type, target.value)
    repository.create_fingerprint(fingerprint)
    return target


@router.get("/targets/new", response_class=HTMLResponse)
def new_target_page(request: Request) -> HTMLResponse:
    """Render the new target HTML form."""
    return templates.TemplateResponse(
        request,
        "targets/new.html",
        {
            "request": request,
            "target_types": sorted(VALID_TARGET_TYPES),
            "execution_modes": sorted(VALID_TARGET_MODES),
            "default_mode": TARGET_MODE_DRY_RUN,
            "error": None,
            "selectable_modules": _selectable_runtime_modules(),
        },
    )


@router.post("/targets/new", response_class=HTMLResponse)
async def create_target_page(request: Request) -> Response:
    """Create a target from the HTML form and redirect to its real detail page."""
    form = await request.form()
    name = str(form.get("name", ""))
    target_type = str(form.get("target_type", ""))
    value = str(form.get("value", ""))
    mode = str(form.get("mode", TARGET_MODE_DRY_RUN))
    allowed_module_values = [str(item) for item in form.getlist("allowed_modules") if str(item).strip()]
    allowed_modules = ",".join(allowed_module_values)
    noise_profile = str(form.get("noise_profile", "normal"))
    evidence_profile = str(form.get("evidence_profile", "standard"))
    require_confirmations = form.get("require_confirmations") in {"on", "true", "1", "yes"}
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        repository = TargetsRepository(session)
        try:
            target = _create_target_from_form(
                repository=repository,
                name=name,
                target_type=target_type,
                value=value,
                mode=mode,
                allowed_modules=allowed_modules,
                noise_profile=noise_profile,
                evidence_profile=evidence_profile,
                require_confirmations=require_confirmations,
            )
        except (ContractError, ValueError) as exc:
            return templates.TemplateResponse(
                request,
                "targets/new.html",
                {
                    "request": request,
                    "target_types": sorted(VALID_TARGET_TYPES),
                    "execution_modes": sorted(VALID_TARGET_MODES),
                    "default_mode": mode,
                    "error": str(exc),
                    "selectable_modules": _selectable_runtime_modules(),
                },
                status_code=400,
            )
        return RedirectResponse(url=f"/targets/{target.target_id}", status_code=303)
    finally:
        session_iterator.close()


def _fingerprint_payload(fingerprint: Any | None) -> dict[str, Any] | None:
    if fingerprint is None:
        return None
    return {
        "normalized_value": fingerprint.normalized_value,
        "tags": json.loads(fingerprint.tags_json),
        "confidence": fingerprint.confidence,
    }


def _target_to_record(target: Any) -> TargetRecord:
    """Convert a database target into a planning record for the HTML detail page."""
    return TargetRecord(
        target_id=target.target_id,
        name=target.name,
        target_type=target.target_type,
        value=target.value,
        normalized_value=target.normalized_value,
        mode=target.mode,
        allowed_modules=json.loads(target.allowed_modules_json),
        limits=json.loads(target.limits_json),
        noise_profile=target.noise_profile,
        evidence_profile=target.evidence_profile,
        require_confirmations=target.require_confirmations,
        metadata=json.loads(target.metadata_json),
        created_by=target.created_by,
        created_at=target.created_at.isoformat() if target.created_at else None,
    )


@router.post("/targets/{target_id}/m01/passive-dns", response_class=HTMLResponse)
def run_target_m01_passive_dns_page(
    request: Request, target_id: str, include_external: bool = Form(False)
) -> HTMLResponse:
    """Run target-bound M01 passive DNS from the target detail page."""
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        repository = TargetsRepository(session)
        target = repository.get_by_target_id(target_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Target not found.")
        fingerprint = repository.get_latest_fingerprint(target_id)
        runtime_registry = get_runtime_registry_snapshot()
        target_record = _target_to_record(target)
        plan = OjoRouter(runtime_registry.registry).plan_target(target=target_record)
        result = None
        error = None
        try:
            result = run_target_passive_dns(target_record, include_external=include_external).to_dict()
        except ValueError as exc:
            error = str(exc)
        return templates.TemplateResponse(
            request,
            "targets/detail.html",
            _target_detail_context(
                request,
                target,
                fingerprint,
                plan,
                runtime_registry,
                target_record,
                m01_passive_dns_result=result,
                m01_passive_dns_error=error,
            ),
        )
    finally:
        session_iterator.close()


@router.post("/targets/{target_id}/m01/laia-review", response_class=HTMLResponse)
def run_target_m01_laia_review_page(
    request: Request, target_id: str, execute_local_ai: bool = Form(False)
) -> HTMLResponse:
    """Run a gated local LaIA/Mistral review from the target detail page."""
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        repository = TargetsRepository(session)
        target = repository.get_by_target_id(target_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Target not found.")
        fingerprint = repository.get_latest_fingerprint(target_id)
        runtime_registry = get_runtime_registry_snapshot()
        target_record = _target_to_record(target)
        plan = OjoRouter(runtime_registry.registry).plan_target(target=target_record)
        error = None
        success = None
        if not execute_local_ai:
            error = "Marca la confirmación execute_local_ai para ejecutar Mistral local."
        else:
            try:
                chatml_prompt = render_m01_target_chatml_prompt(target_record)
                client = _target_mistral_client()
                review_text = client.generate_text(str(chatml_prompt["prompt"]))
                review_path = write_m01_target_ai_review(
                    target_record,
                    model=client.model,
                    prompt_sha256=str(chatml_prompt["prompt_sha256"]),
                    content=review_text,
                )
                success = f"Revision LaIA/Mistral guardada en {review_path.as_posix()}"
            except ConfigurationError as exc:
                error = str(exc)
        return templates.TemplateResponse(
            request,
            "targets/detail.html",
            _target_detail_context(
                request,
                target,
                fingerprint,
                plan,
                runtime_registry,
                target_record,
                m01_laia_review_error=error,
                m01_laia_review_success=success,
            ),
        )
    finally:
        session_iterator.close()


@router.post("/targets/{target_id}/m01/action-plan/write", response_class=HTMLResponse)
def write_target_m01_action_plan_page(request: Request, target_id: str) -> HTMLResponse:
    """Persist the evidence-derived M01 operator plan from the target detail page."""
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        repository = TargetsRepository(session)
        target = repository.get_by_target_id(target_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Target not found.")
        fingerprint = repository.get_latest_fingerprint(target_id)
        runtime_registry = get_runtime_registry_snapshot()
        target_record = _target_to_record(target)
        plan = OjoRouter(runtime_registry.registry).plan_target(target=target_record)
        path = write_m01_action_plan(target_record)
        return templates.TemplateResponse(
            request,
            "targets/detail.html",
            _target_detail_context(
                request,
                target,
                fingerprint,
                plan,
                runtime_registry,
                target_record,
                m01_action_plan_success=f"Plan M01 actualizado en {path.as_posix()}",
            ),
        )
    finally:
        session_iterator.close()


@router.post("/targets/{target_id}/m01/action-board/progress", response_class=HTMLResponse)
def update_target_m01_action_progress_page(
    request: Request,
    target_id: str,
    step_id: str = Form(...),
    status: str = Form(...),
    note: str = Form(""),
) -> HTMLResponse:
    """Record operator-only progress for a current M01 plan action from the target page."""
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        repository = TargetsRepository(session)
        target = repository.get_by_target_id(target_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Target not found.")
        fingerprint = repository.get_latest_fingerprint(target_id)
        runtime_registry = get_runtime_registry_snapshot()
        target_record = _target_to_record(target)
        plan = OjoRouter(runtime_registry.registry).plan_target(target=target_record)
        try:
            update_m01_action_progress(target_record, step_id=step_id, status=status, note=note)
            success = "Estado del paso M01 guardado."
            error = None
        except ValueError as exc:
            success = None
            error = str(exc)
        return templates.TemplateResponse(
            request,
            "targets/detail.html",
            _target_detail_context(
                request, target, fingerprint, plan, runtime_registry, target_record,
                m01_action_progress_error=error, m01_action_progress_success=success,
            ),
        )
    finally:
        session_iterator.close()


@router.post("/targets/{target_id}/start", response_class=HTMLResponse)
async def start_target_product_flow_page(request: Request, target_id: str) -> HTMLResponse:
    """Run the New target → module selection → execution flow from the HTML detail page."""
    form = await request.form()
    selected_techniques = [str(item) for item in form.getlist("selected_techniques") if str(item).strip()]
    mode = str(form.get("mode", TARGET_MODE_DRY_RUN))
    confirmed = form.get("confirmed") in {"on", "true", "1", "yes"}
    allowlisted_target = form.get("allowlisted_target") in {"on", "true", "1", "yes"}
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        repository = TargetsRepository(session)
        target = repository.get_by_target_id(target_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Target not found.")
        fingerprint = repository.get_latest_fingerprint(target_id)
        runtime_registry = get_runtime_registry_snapshot()
        target_record = _target_to_record(target)
        plan = OjoRouter(runtime_registry.registry).plan_target(
            target=target_record,
            confirmed=confirmed,
            allowlisted_target=allowlisted_target,
        )
        error = None
        result = None
        if not selected_techniques:
            error = "Selecciona al menos una técnica runtime lista antes de iniciar."
        else:
            module_by_technique = {step.technique_id: step.module_id for step in plan.runnable_steps}
            selected_modules = sorted({module_by_technique[technique_id] for technique_id in selected_techniques if technique_id in module_by_technique})
            payload = TargetJobStartRequest(
                mode=mode,
                selected_modules=selected_modules,
                selected_techniques=selected_techniques,
                confirmed=confirmed,
                allowlisted_target=allowlisted_target,
                created_by="web_operator",
            )
            start_result = run_target_job_start(target_id, payload, session)
            body = getattr(start_result, "body", None)
            if body is not None:
                result = json.loads(body.decode("utf-8"))
            else:
                result = start_result
        return templates.TemplateResponse(
            request,
            "targets/detail.html",
            _target_detail_context(
                request,
                target,
                fingerprint,
                plan,
                runtime_registry,
                target_record,
                product_flow_result=result,
                product_flow_error=error,
            ),
        )
    finally:
        session_iterator.close()


@router.get("/targets/{target_id}", response_class=HTMLResponse)
def target_detail_page(request: Request, target_id: str) -> HTMLResponse:
    """Render a target detail page with the latest stored fingerprint."""
    session_iterator = get_session()
    try:
        session = next(session_iterator)
        repository = TargetsRepository(session)
        target = repository.get_by_target_id(target_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Target not found.")
        fingerprint = repository.get_latest_fingerprint(target_id)
        runtime_registry = get_runtime_registry_snapshot()
        target_record = _target_to_record(target)
        plan = OjoRouter(runtime_registry.registry).plan_target(target=target_record)
        return templates.TemplateResponse(
            request,
            "targets/detail.html",
            _target_detail_context(request, target, fingerprint, plan, runtime_registry, target_record),
        )
    finally:
        session_iterator.close()
