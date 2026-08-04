"""In-process API rate limiting middleware for Ojo de Dios."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply a fixed-window-per-client limit to API routes.

    The limiter is intentionally local to the process: it protects a single Ojo
    server instance without requiring Redis or another service. Deployments that
    run multiple workers can still place a shared limiter in front of the app;
    this middleware remains an honest last-resort API guard in local/CI mode.
    """

    def __init__(
        self,
        app: Any,
        *,
        enabled: bool = True,
        limit: int = 120,
        window_seconds: int = 60,
        api_prefix: str = "/api/",
    ) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.limit = max(int(limit), 1)
        self.window_seconds = max(int(window_seconds), 1)
        self.api_prefix = api_prefix
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Limit requests before they reach API route handlers."""
        if not self.enabled or not request.url.path.startswith(self.api_prefix):
            return await call_next(request)

        key = self._client_key(request)
        now = monotonic()
        allowed, remaining, retry_after = self._consume(key, now)
        if not allowed:
            return JSONResponse(
                status_code=429,
                headers=self._headers(0, retry_after),
                content={
                    "detail": "API rate limit exceeded.",
                    "rate_limit": {
                        "limit": self.limit,
                        "window_seconds": self.window_seconds,
                        "retry_after_seconds": retry_after,
                    },
                },
            )

        response = await call_next(request)
        for header, value in self._headers(remaining, retry_after).items():
            response.headers[header] = value
        return response

    def _consume(self, key: str, now: float) -> tuple[bool, int, int]:
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._requests[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.limit:
                retry_after = max(int(bucket[0] + self.window_seconds - now) + 1, 1)
                return False, 0, retry_after
            bucket.append(now)
            remaining = max(self.limit - len(bucket), 0)
            retry_after = max(int(bucket[0] + self.window_seconds - now) + 1, 1)
            return True, remaining, retry_after

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
        host = forwarded or (request.client.host if request.client else "unknown")
        return f"{host}:{request.url.path}"

    def _headers(self, remaining: int, retry_after: int) -> dict[str, str]:
        return {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(max(remaining, 0)),
            "X-RateLimit-Window-Seconds": str(self.window_seconds),
            "Retry-After": str(retry_after),
        }
