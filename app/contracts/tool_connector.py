"""Tool connector contracts for Ojo de Dios."""

from dataclasses import dataclass, field
from typing import Any

from app.contracts.manual_required import ManualImplementationRequired


@dataclass
class ToolExecutionRequest:
    """Request to execute a tool connector."""

    tool_name: str
    tool_version: str
    runtime: str
    parameters: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = False
    demo: bool = False


@dataclass
class ToolExecutionResult:
    """Result returned by a tool connector."""

    tool_name: str
    status: str
    stdout: str = ""
    stderr: str = ""
    return_code: int | None = None
    raw_result: dict[str, Any] = field(default_factory=dict)


class BaseToolConnector:
    """Base contract for a user-provided tool connector."""

    tool_name: str = ""
    runtime: str = ""

    def prepare(self, request: ToolExecutionRequest) -> ToolExecutionRequest:
        """Return the request unchanged by default."""
        return request

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Require a private connector implementation by default."""
        raise ManualImplementationRequired(
            "IMPLEMENTACION_USUARIO_REQUERIDA: conecta aquí el conector real de herramienta."
        )
