"""Guarded command runner for approved tool installation steps.

This module can execute an already-built ToolInstallStep, but only when the
caller supplies explicit approval. It uses argv-only subprocess calls, never a
shell, and returns a receipt that can be audited or persisted by higher layers.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.errors import ContractError
from app.core.tool_install_plan import INSTALL_STATUS_READY, ToolInstallStep

INSTALL_EXECUTION_APPROVAL = "APPROVED_EXECUTE_TOOL_INSTALL"
INSTALL_EXECUTION_SKIPPED = "SKIPPED_APPROVAL_REQUIRED"
INSTALL_EXECUTION_BLOCKED = "BLOCKED"
INSTALL_EXECUTION_COMPLETED = "COMPLETED"
INSTALL_EXECUTION_FAILED = "FAILED"
INSTALL_EXECUTION_TIMEOUT = "TIMEOUT"

_SECRET_TEXT_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|authorization)\s*[:=]\s*[^\s]+"),
    re.compile(r"(?i)(bearer)\s+[a-z0-9._~+/=-]+"),
)


@dataclass(frozen=True, slots=True)
class ToolInstallExecutionReceipt:
    """Auditable receipt for one attempted or skipped install step."""

    module_id: str
    tool_id: str
    display_name: str
    status: str
    command_argv: tuple[str, ...]
    started_at: str
    finished_at: str
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    message: str = ""
    execution_performed: bool = False
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "display_name": self.display_name,
            "status": self.status,
            "command_argv": list(self.command_argv),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "return_code": self.return_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "message": self.message,
            "execution_performed": self.execution_performed,
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
        }


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat()


def _redact_text(value: str) -> str:
    redacted = value
    for pattern in _SECRET_TEXT_PATTERNS:
        redacted = pattern.sub(lambda match: match.group(1) + "=<redacted>", redacted)
    return redacted


def _base_receipt(
    step: ToolInstallStep,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    message: str,
    execution_performed: bool = False,
    return_code: int | None = None,
    stdout: str = "",
    stderr: str = "",
) -> ToolInstallExecutionReceipt:
    duration = max((finished_at - started_at).total_seconds(), 0.0)
    return ToolInstallExecutionReceipt(
        module_id=step.module_id,
        tool_id=step.tool_id,
        display_name=step.display_name,
        status=status,
        command_argv=step.command_argv,
        started_at=_iso(started_at),
        finished_at=_iso(finished_at),
        return_code=return_code,
        stdout=_redact_text(stdout),
        stderr=_redact_text(stderr),
        message=message,
        execution_performed=execution_performed,
        duration_seconds=duration,
        metadata={"manager": step.manager, "package_name": step.package_name},
    )


def execute_tool_install_step(
    step: ToolInstallStep,
    approval: str = "",
    timeout_seconds: int = 300,
    cwd: Path | None = None,
) -> ToolInstallExecutionReceipt:
    """Execute one ready install step after explicit approval and return a receipt."""
    started_at = _utc_now()
    if step.status != INSTALL_STATUS_READY:
        finished_at = _utc_now()
        return _base_receipt(
            step,
            INSTALL_EXECUTION_BLOCKED,
            started_at,
            finished_at,
            "Install step is not READY_TO_INSTALL.",
        )
    if not step.command_argv:
        finished_at = _utc_now()
        return _base_receipt(step, INSTALL_EXECUTION_BLOCKED, started_at, finished_at, "Install step has no argv command.")
    if approval != INSTALL_EXECUTION_APPROVAL:
        finished_at = _utc_now()
        return _base_receipt(
            step,
            INSTALL_EXECUTION_SKIPPED,
            started_at,
            finished_at,
            "Explicit install execution approval was not supplied.",
        )
    if timeout_seconds <= 0:
        raise ContractError("Install execution timeout must be positive.")

    try:
        completed = subprocess.run(
            list(step.command_argv),
            capture_output=True,
            check=False,
            cwd=cwd,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        finished_at = _utc_now()
        return _base_receipt(
            step,
            INSTALL_EXECUTION_TIMEOUT,
            started_at,
            finished_at,
            "Install command timed out.",
            execution_performed=True,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
        )
    except OSError as exc:
        finished_at = _utc_now()
        return _base_receipt(
            step,
            INSTALL_EXECUTION_FAILED,
            started_at,
            finished_at,
            f"Install command could not be started: {exc}.",
            execution_performed=False,
        )

    finished_at = _utc_now()
    status = INSTALL_EXECUTION_COMPLETED if completed.returncode == 0 else INSTALL_EXECUTION_FAILED
    message = "Install command completed." if completed.returncode == 0 else "Install command exited with a non-zero code."
    return _base_receipt(
        step,
        status,
        started_at,
        finished_at,
        message,
        execution_performed=True,
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
