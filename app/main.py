"""FastAPI application entry point for Ojo de Dios."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_auth import router as auth_router
from app.api.routes_health import router as health_router
from app.api.routes_kill_switch import router as kill_switch_router
from app.api.routes_modules import router as modules_router
from app.api.routes_rag import router as rag_router
from app.api.routes_chat import router as chat_router
from app.api.routes_targets import router as targets_router
from app.web.routes_auth_pages import router as auth_pages_router
from app.web.routes_chat_pages import router as chat_pages_router
from app.web.routes_modules_pages import router as module_pages_router
from app.web.routes_targets_pages import router as target_pages_router
from app.config import get_settings
from app.core.constants import HEALTH_STATUS_OK
from app.core.kill_switch_middleware import KillSwitchMiddleware
from app.core.rate_limit_middleware import RateLimitMiddleware
from app.core.runtime_bootstrap import bootstrap_runtime


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        """Prepare real runtime directories and database tables on application startup."""
        bootstrap_runtime(settings)
        yield

    fastapi_app = FastAPI(title=settings.product_display_name, lifespan=lifespan)
    fastapi_app.add_middleware(
        RateLimitMiddleware,
        enabled=settings.api_rate_limit_enabled,
        limit=settings.api_rate_limit_requests,
        window_seconds=settings.api_rate_limit_window_seconds,
    )
    fastapi_app.add_middleware(KillSwitchMiddleware)
    fastapi_app.include_router(auth_router)
    fastapi_app.include_router(health_router)
    fastapi_app.include_router(kill_switch_router)
    fastapi_app.include_router(modules_router)
    fastapi_app.include_router(targets_router)
    fastapi_app.include_router(chat_router)
    fastapi_app.include_router(rag_router)
    fastapi_app.mount("/static", StaticFiles(directory="app/static"), name="static")
    fastapi_app.include_router(auth_pages_router)
    fastapi_app.include_router(module_pages_router)
    fastapi_app.include_router(chat_pages_router)
    fastapi_app.include_router(target_pages_router)

    @fastapi_app.get("/")
    def root() -> dict[str, str]:
        """Return the minimal product landing payload."""
        return {
            "product": settings.product_display_name,
            "version": settings.app_version,
            "status": HEALTH_STATUS_OK,
            "next": "/modules",
        }

    return fastapi_app


app = create_app()
