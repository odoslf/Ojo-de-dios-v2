"""Real implementation status summaries for the modules dashboard.

The product catalog and manifests intentionally describe documented modules, not
runtime implementation.  This helper joins the catalog with the concrete
technique registry, documented tools, workspace inspection and M16 readiness so
UI templates can show actual implemented capabilities instead of placeholder
manifest-only readiness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.contracts.technique_contract import (
    STATUS_READY_CONTROLLED,
    STATUS_READY_LOCAL_AI,
    STATUS_READY_PASSIVE,
)
from app.core.module_catalog import get_module_by_id
from app.core.registry_loader import load_registry_from_package
from app.core.technique_catalog import list_module_techniques
from app.core.tool_inventory import list_documented_tools_for_module
from app.core.workspace_state import collect_module_workspace_state

IMPLEMENTED_DASHBOARD_MODULE_IDS = (
    "m01_osint",
    "m03_network_services",
    "m09_scraping_intelligence",
    "m12_orchestration",
    "m15_cloud",
    "m16_ops_quality",
    "m18_honeypots_deception",
)
READY_IMPLEMENTATION_STATUSES = {STATUS_READY_PASSIVE, STATUS_READY_CONTROLLED, STATUS_READY_LOCAL_AI}


@dataclass(frozen=True, slots=True)
class ModuleImplementationStatus:
    """Dashboard-ready status derived from real code and local filesystem state."""

    module_id: str
    display_name: str
    catalog_readiness: str
    documented_technique_count: int
    implemented_technique_count: int
    ready_technique_count: int
    local_ai_technique_count: int
    documented_tool_count: int
    workspace_exists: bool
    workspace_run_count: int
    readiness_status: str
    readiness_message: str
    implementation_statuses: tuple[str, ...]
    source_package: str
    detail_url: str

    @property
    def has_real_logic(self) -> bool:
        return self.implemented_technique_count > 0 or self.module_id == "m16_ops_quality"

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "display_name": self.display_name,
            "catalog_readiness": self.catalog_readiness,
            "documented_technique_count": self.documented_technique_count,
            "implemented_technique_count": self.implemented_technique_count,
            "ready_technique_count": self.ready_technique_count,
            "local_ai_technique_count": self.local_ai_technique_count,
            "documented_tool_count": self.documented_tool_count,
            "workspace_exists": self.workspace_exists,
            "workspace_run_count": self.workspace_run_count,
            "readiness_status": self.readiness_status,
            "readiness_message": self.readiness_message,
            "implementation_statuses": list(self.implementation_statuses),
            "source_package": self.source_package,
            "detail_url": self.detail_url,
            "has_real_logic": self.has_real_logic,
        }


def _registry_status_counts(module_id: str, package_name: str) -> tuple[int, int, int, tuple[str, ...]]:
    registry = load_registry_from_package(package_name, allow_missing=True)
    statuses: list[str] = []
    ready_count = 0
    local_ai_count = 0
    for technique_cls in registry.list_by_module(module_id):
        technique = technique_cls()
        statuses.append(technique.implementation_status)
        if technique.implementation_status in READY_IMPLEMENTATION_STATUSES:
            ready_count += 1
        if technique.implementation_status == STATUS_READY_LOCAL_AI:
            local_ai_count += 1
    return len(statuses), ready_count, local_ai_count, tuple(sorted(set(statuses)))


def build_module_implementation_status(module_id: str) -> ModuleImplementationStatus:
    """Build one real dashboard status row from registry, docs, tools and workspace state."""
    module = get_module_by_id(module_id)
    if module is None:
        raise KeyError(module_id)
    source_package = f"app.modules.{module.module_id}"
    documented_technique_count = len(list_module_techniques(module.module_id)) if module.doc_path else 0
    implemented_count, ready_count, local_ai_count, statuses = _registry_status_counts(module.module_id, source_package)
    documented_tool_count = len(list_documented_tools_for_module(module.module_id))
    workspace_state = collect_module_workspace_state(module.module_id)
    if module.module_id == "m16_ops_quality":
        readiness_status = "READY_READINESS_CHECKS"
        readiness_message = "Readiness calculado por checks reales de M16 en tiempo de renderizado."
    elif implemented_count == 0:
        readiness_status = "MANIFEST_ONLY"
        readiness_message = "Solo hay manifest/documentación; no hay técnicas registradas con lógica real."
    elif ready_count == implemented_count:
        readiness_status = "READY_IMPLEMENTED"
        readiness_message = "Todas las técnicas registradas para este módulo están marcadas como listas/controladas/locales."
    else:
        readiness_status = "PARTIAL_IMPLEMENTATION"
        readiness_message = "Hay técnicas registradas, pero no todas están en estado READY."
    return ModuleImplementationStatus(
        module_id=module.module_id,
        display_name=module.display_name,
        catalog_readiness=module.readiness,
        documented_technique_count=documented_technique_count,
        implemented_technique_count=implemented_count,
        ready_technique_count=ready_count,
        local_ai_technique_count=local_ai_count,
        documented_tool_count=documented_tool_count,
        workspace_exists=workspace_state.workspace_exists,
        workspace_run_count=workspace_state.run_count,
        readiness_status=readiness_status,
        readiness_message=readiness_message,
        implementation_statuses=statuses,
        source_package=source_package,
        detail_url=f"/modules/{module.module_id}",
    )


def build_dashboard_implementation_summary(module_ids: tuple[str, ...] = IMPLEMENTED_DASHBOARD_MODULE_IDS) -> dict[str, Any]:
    """Build aggregate real implementation status for dashboard templates and tests."""
    statuses = tuple(build_module_implementation_status(module_id) for module_id in module_ids)
    return {
        "module_ids": list(module_ids),
        "implemented_module_count": sum(1 for item in statuses if item.has_real_logic),
        "implemented_technique_count": sum(item.implemented_technique_count for item in statuses),
        "ready_technique_count": sum(item.ready_technique_count for item in statuses),
        "local_ai_technique_count": sum(item.local_ai_technique_count for item in statuses),
        "manifest_only_count": sum(1 for item in statuses if item.readiness_status == "MANIFEST_ONLY"),
        "statuses": statuses,
        "execution_implied": False,
    }
