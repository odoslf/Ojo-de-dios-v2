"""Version lock contract helpers for tool version metadata."""

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.errors import ContractError
from app.core.tool_definition import ToolDefinition
from app.core.workspace import normalize_tool_id

VERSION_LOCK_STATUS_LOCKED = "LOCKED"
VERSION_LOCK_STATUS_MISSING = "MISSING"
VERSION_LOCK_STATUS_NEEDS_REVIEW = "NEEDS_REVIEW"
VERSION_LOCK_RECOMMENDED_UNRESOLVED = "unresolved"

VALID_VERSION_LOCK_STATUSES = {
    VERSION_LOCK_STATUS_LOCKED,
    VERSION_LOCK_STATUS_MISSING,
    VERSION_LOCK_STATUS_NEEDS_REVIEW,
}

RUNTIME_WINDOWS = "windows"
RUNTIME_WSL = "wsl"
RUNTIME_DOCKER = "docker"
RUNTIME_HARDWARE = "hardware"
RUNTIME_PYTHON = "python"
RUNTIME_GO = "go"
RUNTIME_NODE = "node"
RUNTIME_CUSTOM = "custom"

VALID_VERSION_LOCK_RUNTIMES = {
    RUNTIME_WINDOWS,
    RUNTIME_WSL,
    RUNTIME_DOCKER,
    RUNTIME_HARDWARE,
    RUNTIME_PYTHON,
    RUNTIME_GO,
    RUNTIME_NODE,
    RUNTIME_CUSTOM,
}

_RUNTIME_BY_TOOL_CATEGORY = {
    "python_package": RUNTIME_PYTHON,
    "node_package": RUNTIME_NODE,
    "docker_image": RUNTIME_DOCKER,
    "hardware": RUNTIME_HARDWARE,
}


@dataclass
class VersionLockEntry:
    """Tool version lock metadata accepted by the persistence layer."""

    tool_id: str
    tool_name: str
    module_id: str
    recommended_version: str
    resolved_version: str = ""
    source_url: str = ""
    runtime: str = RUNTIME_CUSTOM
    binary_hash: str = ""
    locked_at: str | None = None
    status: str = VERSION_LOCK_STATUS_NEEDS_REVIEW


def _utc_isoformat() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_latest_release_lock(value: str) -> bool:
    """Return whether a recommended version requests a future release lock."""
    return value.strip().lower() == "latest-release-lock"


def validate_version_lock_entry(entry: VersionLockEntry) -> None:
    """Validate a version lock entry without resolving external versions."""
    if not entry.tool_id:
        raise ContractError("Tool id cannot be empty.")
    if not entry.tool_name:
        raise ContractError("Tool name cannot be empty.")
    if not entry.module_id:
        raise ContractError("Module id cannot be empty.")
    if not entry.recommended_version:
        raise ContractError("Recommended version cannot be empty.")
    if entry.runtime not in VALID_VERSION_LOCK_RUNTIMES:
        raise ContractError("Invalid version lock runtime.")
    if entry.status not in VALID_VERSION_LOCK_STATUSES:
        raise ContractError("Invalid version lock status.")
    if entry.status == VERSION_LOCK_STATUS_LOCKED:
        if not entry.resolved_version:
            raise ContractError("Locked version requires resolved version.")
        if not entry.locked_at:
            raise ContractError("Locked version requires locked_at.")
    if entry.status == VERSION_LOCK_STATUS_MISSING:
        if entry.resolved_version:
            raise ContractError("Missing version cannot have resolved version.")
        if entry.binary_hash:
            raise ContractError("Missing version cannot have binary hash.")
    if entry.source_url and not (entry.source_url.startswith("http://") or entry.source_url.startswith("https://")):
        raise ContractError("Source URL must start with http:// or https://.")
    if entry.binary_hash and len(entry.binary_hash) < 16:
        raise ContractError("Binary hash is too short.")


def create_missing_lock(
    tool_id: str,
    tool_name: str,
    module_id: str,
    recommended_version: str,
    runtime: str = RUNTIME_CUSTOM,
    source_url: str = "",
) -> VersionLockEntry:
    """Create a missing version lock entry without checking the local system."""
    entry = VersionLockEntry(
        tool_id=tool_id,
        tool_name=tool_name,
        module_id=module_id,
        recommended_version=recommended_version,
        resolved_version="",
        source_url=source_url,
        runtime=runtime,
        binary_hash="",
        locked_at=_utc_isoformat(),
        status=VERSION_LOCK_STATUS_MISSING,
    )
    validate_version_lock_entry(entry)
    return entry


def create_locked_entry(
    tool_id: str,
    tool_name: str,
    module_id: str,
    recommended_version: str,
    resolved_version: str,
    runtime: str,
    source_url: str = "",
    binary_hash: str = "",
) -> VersionLockEntry:
    """Create a locked entry from explicitly provided version metadata."""
    entry = VersionLockEntry(
        tool_id=tool_id,
        tool_name=tool_name,
        module_id=module_id,
        recommended_version=recommended_version,
        resolved_version=resolved_version,
        source_url=source_url,
        runtime=runtime,
        binary_hash=binary_hash,
        locked_at=_utc_isoformat(),
        status=VERSION_LOCK_STATUS_LOCKED,
    )
    validate_version_lock_entry(entry)
    return entry


def create_needs_review_entry(
    tool_id: str,
    tool_name: str,
    module_id: str,
    recommended_version: str,
    resolved_version: str = "",
    runtime: str = RUNTIME_CUSTOM,
    source_url: str = "",
    binary_hash: str = "",
) -> VersionLockEntry:
    """Create a needs-review entry without resolving version metadata."""
    entry = VersionLockEntry(
        tool_id=tool_id,
        tool_name=tool_name,
        module_id=module_id,
        recommended_version=recommended_version,
        resolved_version=resolved_version,
        source_url=source_url,
        runtime=runtime,
        binary_hash=binary_hash,
        locked_at=_utc_isoformat(),
        status=VERSION_LOCK_STATUS_NEEDS_REVIEW,
    )
    validate_version_lock_entry(entry)
    return entry


def version_lock_id_for_tool(module_id: str, tool_id: str) -> str:
    """Return a stable module-scoped VersionLock id for a tool."""
    if not module_id.strip():
        raise ContractError("Module id cannot be empty.")
    return f"{module_id}/{normalize_tool_id(tool_id)}"


def runtime_for_tool_definition(definition: ToolDefinition) -> str:
    """Map a validated tool definition into a VersionLock runtime bucket."""
    return _RUNTIME_BY_TOOL_CATEGORY.get(definition.category, RUNTIME_CUSTOM)


def create_needs_review_lock_from_tool_definition(
    definition: ToolDefinition,
    module_id: str | None = None,
) -> VersionLockEntry:
    """Create a needs-review VersionLock entry from a validated tool definition."""
    selected_module_id = module_id or (definition.module_ids[0] if definition.module_ids else "")
    if selected_module_id not in definition.module_ids:
        raise ContractError("VersionLock module id must be present in the tool definition.")
    recommended_version = definition.expected_version or VERSION_LOCK_RECOMMENDED_UNRESOLVED
    return create_needs_review_entry(
        tool_id=definition.versionlock_id or version_lock_id_for_tool(selected_module_id, definition.tool_id),
        tool_name=definition.display_name,
        module_id=selected_module_id,
        recommended_version=recommended_version,
        runtime=runtime_for_tool_definition(definition),
        source_url=definition.source_url or "",
    )
