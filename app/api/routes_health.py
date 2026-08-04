"""Health route for the Ojo de Dios API."""

from fastapi import APIRouter

from app.config import get_settings
from app.core.constants import HEALTH_STATUS_OK
from app.core.runtime_bootstrap import collect_runtime_bootstrap_status
from app.core.runtime_registry import get_runtime_registry_snapshot

router = APIRouter()


@router.get("/api/health")
def health() -> dict[str, str]:
    """Return a minimal application health response."""
    settings = get_settings()
    return {
        "status": HEALTH_STATUS_OK,
        "product_internal_name": settings.product_internal_name,
        "product_display_name": settings.product_display_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "default_execution_mode": settings.default_execution_mode,
    }


@router.get("/api/health/runtime")
def runtime_health() -> dict[str, object]:
    """Return runtime health details needed before real technique execution."""
    settings = get_settings()
    registry_snapshot = get_runtime_registry_snapshot()
    return {
        "status": HEALTH_STATUS_OK if registry_snapshot.ready else "degraded",
        "product_internal_name": settings.product_internal_name,
        "product_display_name": settings.product_display_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "default_execution_mode": settings.default_execution_mode,
        "registry": registry_snapshot.to_status_payload(),
        "bootstrap": collect_runtime_bootstrap_status(settings).to_dict(),
    }
