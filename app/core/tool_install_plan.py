"""Non-executing installation plan builders for registered tools.

The planner converts validated ToolDefinition metadata into explicit argv arrays
that an operator can review before any installer is run. It does not execute,
install, download, or mark tools ready.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.errors import ContractError
from app.core.module_catalog import require_module_by_id
from app.core.tool_definition import ToolDefinition
from app.core.tool_registry import load_module_tool_registry

INSTALL_STATUS_READY = "READY_TO_INSTALL"
INSTALL_STATUS_NEEDS_METADATA = "NEEDS_METADATA"
INSTALL_STATUS_EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
INSTALL_STATUS_HARDWARE_REQUIRED = "HARDWARE_REQUIRED"
INSTALL_STATUS_UNSUPPORTED = "UNSUPPORTED"

INSTALL_MANAGER_APT = "apt"
INSTALL_MANAGER_PIP = "pip"
INSTALL_MANAGER_NPM = "npm"
INSTALL_MANAGER_DOCKER = "docker"
INSTALL_MANAGER_NONE = "none"

_INSTALLABLE_BINARY_RUNTIMES = {"linux", "kali", "kali_wsl", "wsl", "debian", "ubuntu"}


@dataclass(frozen=True, slots=True)
class ToolInstallStep:
    """One reviewable install step for a registered tool definition."""

    module_id: str
    tool_id: str
    display_name: str
    status: str
    manager: str
    command_argv: tuple[str, ...] = ()
    package_name: str = ""
    requires_network: bool = True
    requires_sudo: bool = False
    execution_performed: bool = False
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "tool_id": self.tool_id,
            "display_name": self.display_name,
            "status": self.status,
            "manager": self.manager,
            "command_argv": list(self.command_argv),
            "package_name": self.package_name,
            "requires_network": self.requires_network,
            "requires_sudo": self.requires_sudo,
            "execution_performed": self.execution_performed,
            "reason": self.reason,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class ModuleToolInstallPlan:
    """Reviewable install plan for all registered tools in one module."""

    module_id: str
    steps: tuple[ToolInstallStep, ...]
    execution_performed: bool = False

    @property
    def count(self) -> int:
        return len(self.steps)

    @property
    def ready_count(self) -> int:
        return sum(1 for step in self.steps if step.status == INSTALL_STATUS_READY)

    @property
    def needs_metadata_count(self) -> int:
        return sum(1 for step in self.steps if step.status == INSTALL_STATUS_NEEDS_METADATA)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "steps": [step.to_dict() for step in self.steps],
            "count": self.count,
            "ready_count": self.ready_count,
            "needs_metadata_count": self.needs_metadata_count,
            "execution_performed": self.execution_performed,
        }


def _metadata_value(definition: ToolDefinition, *keys: str) -> str:
    for key in keys:
        value = definition.metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _versioned_package(package_name: str, expected_version: str | None) -> str:
    if not expected_version or expected_version == "latest-release-lock":
        return package_name
    return f"{package_name}=={expected_version}"


def _step(
    definition: ToolDefinition,
    module_id: str,
    status: str,
    manager: str,
    reason: str,
    command_argv: tuple[str, ...] = (),
    package_name: str = "",
    requires_sudo: bool = False,
) -> ToolInstallStep:
    return ToolInstallStep(
        module_id=module_id,
        tool_id=definition.tool_id,
        display_name=definition.display_name,
        status=status,
        manager=manager,
        command_argv=command_argv,
        package_name=package_name,
        requires_sudo=requires_sudo,
        reason=reason,
        metadata={
            "category": definition.category,
            "runtime": definition.runtime,
            "source_url": definition.source_url,
            "expected_version": definition.expected_version,
        },
    )


def build_tool_install_step(definition: ToolDefinition, module_id: str | None = None) -> ToolInstallStep:
    """Build a reviewable install step for one validated tool definition."""
    selected_module_id = module_id or (definition.module_ids[0] if definition.module_ids else "")
    if selected_module_id not in definition.module_ids:
        raise ContractError("Install plan module id must be present in the tool definition.")

    if definition.category == "binary_tool":
        package_name = _metadata_value(definition, "kali_package_name", "apt_package_name", "package_name")
        if definition.runtime not in _INSTALLABLE_BINARY_RUNTIMES:
            return _step(
                definition,
                selected_module_id,
                INSTALL_STATUS_UNSUPPORTED,
                INSTALL_MANAGER_NONE,
                "Binary tool runtime is not an apt-compatible Linux/Kali runtime.",
            )
        if not package_name:
            return _step(
                definition,
                selected_module_id,
                INSTALL_STATUS_NEEDS_METADATA,
                INSTALL_MANAGER_APT,
                "Missing kali_package_name/apt_package_name metadata.",
            )
        return _step(
            definition,
            selected_module_id,
            INSTALL_STATUS_READY,
            INSTALL_MANAGER_APT,
            "APT install command is ready for operator review.",
            command_argv=("sudo", "apt-get", "install", "-y", package_name),
            package_name=package_name,
            requires_sudo=True,
        )

    if definition.category == "python_package":
        package_name = _metadata_value(definition, "python_package_name", "package_name") or definition.tool_id
        return _step(
            definition,
            selected_module_id,
            INSTALL_STATUS_READY,
            INSTALL_MANAGER_PIP,
            "Python package install command is ready for operator review.",
            command_argv=("python", "-m", "pip", "install", _versioned_package(package_name, definition.expected_version)),
            package_name=package_name,
        )

    if definition.category == "node_package":
        package_name = _metadata_value(definition, "node_package_name", "npm_package_name", "package_name") or definition.tool_id
        return _step(
            definition,
            selected_module_id,
            INSTALL_STATUS_READY,
            INSTALL_MANAGER_NPM,
            "Node package install command is ready for operator review.",
            command_argv=("npm", "install", "-g", package_name),
            package_name=package_name,
        )

    if definition.category == "docker_image":
        package_name = _metadata_value(definition, "docker_image", "image", "package_name")
        if not package_name:
            return _step(
                definition,
                selected_module_id,
                INSTALL_STATUS_NEEDS_METADATA,
                INSTALL_MANAGER_DOCKER,
                "Missing docker_image metadata.",
            )
        return _step(
            definition,
            selected_module_id,
            INSTALL_STATUS_READY,
            INSTALL_MANAGER_DOCKER,
            "Docker pull command is ready for operator review.",
            command_argv=("docker", "pull", package_name),
            package_name=package_name,
        )

    if definition.category in {"cloud_api", "external_ai"}:
        return _step(
            definition,
            selected_module_id,
            INSTALL_STATUS_EXTERNAL_SERVICE,
            INSTALL_MANAGER_NONE,
            "External service/API tools require credentials and connector configuration, not local installation.",
        )

    if definition.category == "hardware":
        return _step(
            definition,
            selected_module_id,
            INSTALL_STATUS_HARDWARE_REQUIRED,
            INSTALL_MANAGER_NONE,
            "Hardware-backed tools require physical device availability before install planning.",
        )

    return _step(
        definition,
        selected_module_id,
        INSTALL_STATUS_NEEDS_METADATA,
        INSTALL_MANAGER_NONE,
        "Tool definition is documented but does not yet include installable package metadata.",
    )


def build_module_tool_install_plan(module_id: str) -> ModuleToolInstallPlan:
    """Build a non-executing install plan from one module's registered tools."""
    module = require_module_by_id(module_id)
    registry = load_module_tool_registry(module.module_id)
    steps = tuple(build_tool_install_step(definition, module.module_id) for definition in registry.list_all())
    return ModuleToolInstallPlan(module_id=module.module_id, steps=steps)
