"""Local ToolHealth checks connected to VersionLock metadata.

ToolHealth is deliberately local and non-invasive: it checks whether an expected
executable exists and optionally runs an explicit version command without shell
expansion. It never installs tools, never updates VersionLock automatically, and
never marks a tool ready when version/approval information is missing.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from shutil import which

from app.core.version_lock import (
    VERSION_LOCK_STATUS_LOCKED,
    VERSION_LOCK_STATUS_MISSING,
    VERSION_LOCK_STATUS_NEEDS_REVIEW,
    VersionLockEntry,
)

TOOL_HEALTH_READY_CONTROLLED = "READY_CONTROLLED"
TOOL_HEALTH_MISSING_TOOL = "MISSING_TOOL"
TOOL_HEALTH_VERSION_UNKNOWN = "VERSION_UNKNOWN"
TOOL_HEALTH_VERSION_LOCKED = "VERSION_LOCKED"
TOOL_HEALTH_APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
TOOL_HEALTH_FAILED = "FAILED"

VALID_TOOL_HEALTH_STATUSES = {
    TOOL_HEALTH_READY_CONTROLLED,
    TOOL_HEALTH_MISSING_TOOL,
    TOOL_HEALTH_VERSION_UNKNOWN,
    TOOL_HEALTH_VERSION_LOCKED,
    TOOL_HEALTH_APPROVAL_REQUIRED,
    TOOL_HEALTH_FAILED,
}


@dataclass(frozen=True, slots=True)
class ToolHealthSpec:
    """Local healthcheck specification for one tool."""

    tool_id: str
    executable: str
    version_args: tuple[str, ...] = ()
    timeout_seconds: int = 10
    requires_approval: bool = False


@dataclass(frozen=True, slots=True)
class ToolHealthResult:
    """ToolHealth result suitable for API/panel display."""

    tool_id: str
    tool_name: str
    module_id: str
    status: str
    executable: str
    executable_path: str = ""
    recommended_version: str = ""
    resolved_version: str = ""
    version_output: str = ""
    message: str = ""
    version_lock_status: str = ""
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe ToolHealth result."""
        return {
            "tool_id": self.tool_id,
            "tool_name": self.tool_name,
            "module_id": self.module_id,
            "status": self.status,
            "executable": self.executable,
            "executable_path": self.executable_path,
            "recommended_version": self.recommended_version,
            "resolved_version": self.resolved_version,
            "version_output": self.version_output,
            "message": self.message,
            "version_lock_status": self.version_lock_status,
            "details": self.details,
        }


def _resolve_executable(executable: str) -> str:
    """Resolve an executable name or explicit path without shell expansion."""
    if os.sep in executable or (os.altsep and os.altsep in executable):
        path = Path(executable)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        return ""
    return which(executable) or ""


def _run_version_command(executable_path: str, version_args: tuple[str, ...], timeout_seconds: int) -> tuple[str, str]:
    """Run an explicit version command and return output/error strings."""
    if not version_args:
        return "", ""
    try:
        completed = subprocess.run(
            [executable_path, *version_args],
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return "", str(error)
    output = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
    if completed.returncode != 0:
        return output, f"Version command exited with code {completed.returncode}."
    return output, ""


def check_tool_health(spec: ToolHealthSpec, version_lock: VersionLockEntry) -> ToolHealthResult:
    """Check one tool against local executable state and VersionLock metadata."""
    executable_path = _resolve_executable(spec.executable)
    base = {
        "tool_id": version_lock.tool_id,
        "tool_name": version_lock.tool_name,
        "module_id": version_lock.module_id,
        "executable": spec.executable,
        "recommended_version": version_lock.recommended_version,
        "resolved_version": version_lock.resolved_version,
        "version_lock_status": version_lock.status,
    }
    if version_lock.status == VERSION_LOCK_STATUS_MISSING or not executable_path:
        return ToolHealthResult(
            **base,
            status=TOOL_HEALTH_MISSING_TOOL,
            message="Tool executable is missing or VersionLock marks it as missing.",
        )

    version_output, version_error = _run_version_command(executable_path, spec.version_args, spec.timeout_seconds)
    if version_error:
        return ToolHealthResult(
            **base,
            status=TOOL_HEALTH_VERSION_UNKNOWN,
            executable_path=executable_path,
            version_output=version_output,
            message="Tool exists but version command could not be confirmed.",
            details={"error": version_error},
        )

    if version_lock.status == VERSION_LOCK_STATUS_NEEDS_REVIEW or spec.requires_approval:
        return ToolHealthResult(
            **base,
            status=TOOL_HEALTH_APPROVAL_REQUIRED,
            executable_path=executable_path,
            version_output=version_output,
            message="Tool exists but VersionLock or policy requires review before controlled use.",
        )

    if version_lock.status == VERSION_LOCK_STATUS_LOCKED:
        if not spec.version_args:
            return ToolHealthResult(
                **base,
                status=TOOL_HEALTH_VERSION_LOCKED,
                executable_path=executable_path,
                message="Tool exists and VersionLock is locked; no local version command was configured.",
            )
        if version_lock.resolved_version and version_lock.resolved_version not in version_output:
            return ToolHealthResult(
                **base,
                status=TOOL_HEALTH_VERSION_UNKNOWN,
                executable_path=executable_path,
                version_output=version_output,
                message="Tool exists but local version output does not match the locked resolved version.",
            )
        return ToolHealthResult(
            **base,
            status=TOOL_HEALTH_READY_CONTROLLED,
            executable_path=executable_path,
            version_output=version_output,
            message="Tool exists and local version output matches VersionLock.",
        )

    return ToolHealthResult(
        **base,
        status=TOOL_HEALTH_FAILED,
        executable_path=executable_path,
        version_output=version_output,
        message="ToolHealth reached an unsupported VersionLock state.",
    )
