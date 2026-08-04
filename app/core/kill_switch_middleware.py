"""Global kill-switch middleware for unsafe execution/mutation routes."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.kill_switch import get_kill_switch_status

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
KILL_SWITCH_EXEMPT_PREFIXES = (
    "/api/kill-switch",
    "/api/auth",
    "/login",
    "/logout",
)


class KillSwitchMiddleware(BaseHTTPMiddleware):
    """Block unsafe non-exempt routes while the process-global kill switch is active."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.method.upper() in UNSAFE_METHODS and not request.url.path.startswith(KILL_SWITCH_EXEMPT_PREFIXES):
            kill_status = get_kill_switch_status()
            if kill_status.active:
                return JSONResponse(
                    status_code=status.HTTP_423_LOCKED,
                    content={
                        "detail": "Global kill switch is active; unsafe execution and mutation routes are blocked.",
                        "kill_switch": {
                            "status": kill_status.status,
                            "active": kill_status.active,
                            "reason": kill_status.reason,
                            "activated_by": kill_status.activated_by,
                            "activated_at": kill_status.activated_at,
                        },
                    },
                )
        return await call_next(request)
