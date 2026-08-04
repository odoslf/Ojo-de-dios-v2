"""HTML pages for module catalog and M16 readiness."""

from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.core.module_catalog import get_module_by_id, list_modules
from app.core.module_dashboard_status import (
    build_dashboard_implementation_summary,
    build_module_implementation_status,
)
from app.core.knowledge_base import build_knowledge_base, read_knowledge_status
from app.core.m01_findings import derive_m01_passive_findings
from app.core.osint_domain_snapshot import build_passive_domain_snapshot, write_domain_snapshot
from app.core.technique_catalog import list_module_techniques, summarize_module_techniques
from app.core.tool_install_plan import build_module_tool_install_plan
from app.core.tool_inventory import list_documented_tools_for_module, load_documented_tool_inventory
from app.core.workspace_bootstrap import bootstrap_module_workspace
from app.core.workspace_state import collect_module_workspace_state
from app.core.windows_first_run import build_first_run_report, write_first_run_status
from app.core.windows_station_manifest import build_windows_station_manifest
from app.modules.m16_ops_quality.status import build_m16_readiness_report, read_m16_readiness_history, run_m16_operational_action, write_runtime_status
from app.modules.m18_honeypots_deception.techniques import build_ioc_event_timeline
from app.modules.registry import ModuleManifestError, load_module_manifest

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _settings_to_m16_env() -> dict[str, str]:
    """Convert current settings into M16 readiness flags for page rendering."""
    settings = get_settings()
    return {
        "AI_ENABLED": "1" if settings.ai_enabled else "0",
        "MISTRAL_ENABLED": "1" if settings.mistral_enabled else "0",
        "ANGEL_ENABLED": "1" if settings.angel_enabled else "0",
        "MISTRAL_MODEL": settings.mistral_model,
        "DEEPSEEK_API_KEY": settings.deepseek_api_key,
    }


def _knowledge_status_for_page() -> dict[str, object]:
    try:
        return read_knowledge_status()
    except FileNotFoundError:
        return {"status": "NOT_BUILT", "message": "Base de conocimiento local no construida todavía."}


@router.get("/ops/m16/first-run", response_class=HTMLResponse)
def m16_first_run_page(request: Request) -> HTMLResponse:
    """Render the GitHub ZIP first-run preflight page."""
    report = build_first_run_report()
    return templates.TemplateResponse(
        request,
        "modules/m16_first_run.html",
        {"request": request, "first_run": report, "action_result": None},
    )


@router.post("/ops/m16/first-run/write", response_class=HTMLResponse)
def write_m16_first_run_page(request: Request) -> HTMLResponse:
    """Persist the GitHub ZIP first-run preflight report from the web UI."""
    report = build_first_run_report()
    status_path = write_first_run_status(report)
    return templates.TemplateResponse(
        request,
        "modules/m16_first_run.html",
        {
            "request": request,
            "first_run": report,
            "action_result": {"status": "FIRST_RUN_WRITTEN", "message": f"Estado guardado en {status_path.relative_to(Path.cwd()).as_posix() if status_path.is_absolute() and Path.cwd() in status_path.parents else status_path.as_posix()}."},
        },
    )


@router.get("/ops/m16", response_class=HTMLResponse)
def m16_control_center_page(request: Request) -> HTMLResponse:
    """Render the M16 control center with real local status and safe actions."""
    readiness = build_m16_readiness_report(env=_settings_to_m16_env())
    return templates.TemplateResponse(
        request,
        "modules/m16_control_center.html",
        {
            "request": request,
            "readiness": readiness,
            "knowledge_status": _knowledge_status_for_page(),
            "station_manifest": build_windows_station_manifest(),
            "readiness_history": read_m16_readiness_history(limit=10),
            "action_result": None,
        },
    )


@router.post("/ops/m16/readiness/write", response_class=HTMLResponse)
def write_m16_readiness_page(request: Request) -> HTMLResponse:
    """Persist M16 readiness from the web control center without external calls."""
    readiness = build_m16_readiness_report(env=_settings_to_m16_env())
    status_path = write_runtime_status(readiness)
    return templates.TemplateResponse(
        request,
        "modules/m16_control_center.html",
        {
            "request": request,
            "readiness": readiness,
            "knowledge_status": _knowledge_status_for_page(),
            "station_manifest": build_windows_station_manifest(),
            "readiness_history": read_m16_readiness_history(limit=10),
            "action_result": {"status": "READY_WRITTEN", "message": f"Readiness guardado en {status_path.relative_to(Path.cwd()).as_posix() if status_path.is_absolute() and Path.cwd() in status_path.parents else status_path.as_posix()}."},
        },
    )


@router.post("/ops/m16/knowledge/build", response_class=HTMLResponse)
def build_m16_knowledge_page(request: Request) -> HTMLResponse:
    """Build docs-only local knowledge artifacts from the web control center."""
    knowledge_status = build_knowledge_base(repo_root=Path.cwd(), output_dir=Path("storage/knowledge"), mode="docs-only")
    readiness = build_m16_readiness_report(env=_settings_to_m16_env())
    return templates.TemplateResponse(
        request,
        "modules/m16_control_center.html",
        {
            "request": request,
            "readiness": readiness,
            "knowledge_status": knowledge_status,
            "station_manifest": build_windows_station_manifest(),
            "readiness_history": read_m16_readiness_history(limit=10),
            "action_result": {"status": "KNOWLEDGE_BUILT", "message": "Base de conocimiento local docs-only construida sin llamadas externas."},
        },
    )


@router.post("/ops/m16/actions/{action_id}", response_class=HTMLResponse)
def run_m16_action_page(request: Request, action_id: str) -> HTMLResponse:
    """Run a guided operational action from the M16 control-center buttons."""
    result = run_m16_operational_action(action_id, repo_root=Path.cwd(), env=_settings_to_m16_env())
    readiness = build_m16_readiness_report(env=_settings_to_m16_env())
    return templates.TemplateResponse(
        request,
        "modules/m16_control_center.html",
        {
            "request": request,
            "readiness": readiness,
            "knowledge_status": _knowledge_status_for_page(),
            "station_manifest": build_windows_station_manifest(),
            "readiness_history": read_m16_readiness_history(limit=10),
            "action_result": {"status": result.status, "message": result.message},
        },
    )


@router.get("/modules", response_class=HTMLResponse)
def modules_dashboard(request: Request) -> HTMLResponse:
    """Render the product module catalog and current M16 readiness."""
    modules = list_modules(include_reserved=True)
    readiness = build_m16_readiness_report(env=_settings_to_m16_env())
    implementation_summary = build_dashboard_implementation_summary()
    technique_summary = summarize_module_techniques(include_reserved=True)
    documented_tools = load_documented_tool_inventory()
    official_count = len([module for module in modules if module.official])
    reserved_count = len([module for module in modules if module.reserved])
    readiness_component_count = len(readiness.components)
    ready_statuses = {"READY_CONTROLLED", "READY_LOCAL_AI", "LAB_WORKSPACE_READY"}
    readiness_problem_count = len(
        [component for component in readiness.components if component.status not in ready_statuses]
    )
    return templates.TemplateResponse(
        request,
        "modules/index.html",
        {
            "request": request,
            "modules": modules,
            "readiness": readiness,
            "official_count": official_count,
            "reserved_count": reserved_count,
            "technique_total": technique_summary["total_techniques"],
            "documented_tool_count": len(documented_tools),
            "readiness_component_count": readiness_component_count,
            "readiness_problem_count": readiness_problem_count,
            "implementation_summary": implementation_summary,
            "implemented_statuses": implementation_summary["statuses"],
        },
    )


@router.get("/modules/m01_osint/passive-dns", response_class=HTMLResponse)
def m01_passive_dns_page(request: Request) -> HTMLResponse:
    """Render the passive DNS OSINT form for M01."""
    module = get_module_by_id("m01_osint")
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    return templates.TemplateResponse(
        request,
        "modules/m01_passive_dns.html",
        {
            "request": request,
            "module": module,
            "snapshot": None,
            "artifact_path": None,
            "error": None,
            "include_external": False,
            "findings": (),
        },
    )


@router.post("/modules/m01_osint/passive-dns", response_class=HTMLResponse)
def run_m01_passive_dns_page(
    request: Request, domain: str = Form(...), include_external: bool = Form(False)
) -> HTMLResponse:
    """Run a passive DNS-only M01 lookup from the web form and persist the result."""
    module = get_module_by_id("m01_osint")
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    snapshot = None
    artifact_path = None
    error = None
    findings = ()
    try:
        snapshot = build_passive_domain_snapshot(domain, include_external=include_external)
        artifact_path = write_domain_snapshot(snapshot).as_posix()
        findings = derive_m01_passive_findings(snapshot)
    except ValueError as exc:
        error = str(exc)
    return templates.TemplateResponse(
        request,
        "modules/m01_passive_dns.html",
        {
            "request": request,
            "module": module,
            "snapshot": snapshot,
            "artifact_path": artifact_path,
            "error": error,
            "include_external": include_external,
            "findings": findings,
        },
    )


@router.get("/modules/{module_id}", response_class=HTMLResponse)
def module_detail_page(request: Request, module_id: str) -> HTMLResponse:
    """Render one module with its real catalog, tool, technique and workspace state."""
    module = get_module_by_id(module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    try:
        manifest = load_module_manifest(module.module_id)
    except ModuleManifestError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    techniques = list_module_techniques(module.module_id)
    documented_tools = list_documented_tools_for_module(module.module_id)
    install_plan = build_module_tool_install_plan(module.module_id)
    workspace_state = collect_module_workspace_state(module.module_id)
    implementation_status = build_module_implementation_status(module.module_id)
    m18_ioc_timeline = None
    if module.module_id == "m18_honeypots_deception":
        m18_ioc_timeline = build_ioc_event_timeline(Path("storage/workspaces/m18_honeypots_deception/ioc_history.sqlite3"), limit=25)
    return templates.TemplateResponse(
        request,
        "modules/detail.html",
        {
            "request": request,
            "module": module,
            "manifest": manifest,
            "techniques": techniques,
            "documented_tools": documented_tools,
            "install_plan": install_plan,
            "workspace_state": workspace_state,
            "implementation_status": implementation_status,
            "m18_ioc_timeline": m18_ioc_timeline,
        },
    )


@router.get("/modules/{module_id}/workspace", response_class=HTMLResponse)
def module_workspace_page(request: Request, module_id: str) -> HTMLResponse:
    """Render filesystem workspace state for one module without modifying files."""
    module = get_module_by_id(module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    documented_tools = list_documented_tools_for_module(module.module_id)
    workspace_state = collect_module_workspace_state(module.module_id)
    implementation_status = build_module_implementation_status(module.module_id)
    m18_ioc_timeline = None
    if module.module_id == "m18_honeypots_deception":
        m18_ioc_timeline = build_ioc_event_timeline(Path("storage/workspaces/m18_honeypots_deception/ioc_history.sqlite3"), limit=25)
    return templates.TemplateResponse(
        request,
        "modules/workspace.html",
        {
            "request": request,
            "module": module,
            "documented_tools": documented_tools,
            "workspace_state": workspace_state,
            "implementation_status": implementation_status,
            "bootstrap_result": None,
        },
    )


@router.post("/modules/{module_id}/workspace/bootstrap", response_class=HTMLResponse)
def bootstrap_module_workspace_page(request: Request, module_id: str) -> HTMLResponse:
    """Bootstrap one module workspace from the page without installing or running tools."""
    module = get_module_by_id(module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found.")
    bootstrap_result = bootstrap_module_workspace(module.module_id, include_documented_tools=True)
    documented_tools = list_documented_tools_for_module(module.module_id)
    workspace_state = collect_module_workspace_state(module.module_id)
    implementation_status = build_module_implementation_status(module.module_id)
    m18_ioc_timeline = None
    if module.module_id == "m18_honeypots_deception":
        m18_ioc_timeline = build_ioc_event_timeline(Path("storage/workspaces/m18_honeypots_deception/ioc_history.sqlite3"), limit=25)
    return templates.TemplateResponse(
        request,
        "modules/workspace.html",
        {
            "request": request,
            "module": module,
            "documented_tools": documented_tools,
            "workspace_state": workspace_state,
            "implementation_status": implementation_status,
            "bootstrap_result": bootstrap_result,
        },
    )
