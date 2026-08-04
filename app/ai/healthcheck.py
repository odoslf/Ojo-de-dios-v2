"""Lightweight AI configuration healthcheck."""

from dataclasses import dataclass


@dataclass
class AIHealthStatus:
    """AI backend configuration status."""

    enabled: bool
    backend: str
    model: str
    configured: bool
    status: str
    message: str


def check_ai_health(
    enabled: bool,
    backend: str,
    model: str,
    base_url: str,
) -> AIHealthStatus:
    """Check AI configuration without contacting the runtime backend."""
    if not enabled:
        return AIHealthStatus(
            enabled=False,
            backend=backend,
            model=model,
            configured=False,
            status="disabled",
            message="AI is disabled.",
        )
    if backend != "ollama":
        return AIHealthStatus(
            enabled=True,
            backend=backend,
            model=model,
            configured=False,
            status="unsupported_backend",
            message="Unsupported AI backend.",
        )
    if not base_url:
        return AIHealthStatus(
            enabled=True,
            backend=backend,
            model=model,
            configured=False,
            status="missing_config",
            message="AI backend base URL is missing.",
        )
    return AIHealthStatus(
        enabled=True,
        backend=backend,
        model=model,
        configured=True,
        status="configured",
        message="AI backend configured. Runtime availability is not checked in this lightweight healthcheck.",
    )
