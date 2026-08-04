"""Tool install plan contract tests."""

from app.core.tool_definition import ToolDefinition
from app.core.tool_install_plan import (
    INSTALL_MANAGER_APT,
    INSTALL_MANAGER_DOCKER,
    INSTALL_MANAGER_NONE,
    INSTALL_MANAGER_PIP,
    INSTALL_STATUS_EXTERNAL_SERVICE,
    INSTALL_STATUS_HARDWARE_REQUIRED,
    INSTALL_STATUS_NEEDS_METADATA,
    INSTALL_STATUS_READY,
    build_module_tool_install_plan,
    build_tool_install_step,
)


def _definition(**overrides) -> ToolDefinition:
    data = {
        "tool_id": "nmap",
        "display_name": "Nmap",
        "category": "binary_tool",
        "module_ids": ("m01_osint",),
        "runtime": "kali_wsl",
        "workspace_path": "storage/workspaces/m01_osint/tools/nmap",
        "approved_status": "documented_planned",
        "healthcheck_method": "command_version",
        "execution_implied": False,
        "metadata": {"kali_package_name": "nmap"},
    }
    data.update(overrides)
    return ToolDefinition(**data)


def test_binary_kali_tool_with_package_metadata_builds_apt_argv_without_execution() -> None:
    step = build_tool_install_step(_definition())

    assert step.status == INSTALL_STATUS_READY
    assert step.manager == INSTALL_MANAGER_APT
    assert step.command_argv == ("sudo", "apt-get", "install", "-y", "nmap")
    assert step.requires_sudo is True
    assert step.execution_performed is False


def test_binary_tool_without_package_metadata_requires_metadata() -> None:
    step = build_tool_install_step(_definition(metadata={}))

    assert step.status == INSTALL_STATUS_NEEDS_METADATA
    assert step.manager == INSTALL_MANAGER_APT
    assert step.command_argv == ()


def test_python_package_install_step_uses_expected_version() -> None:
    step = build_tool_install_step(
        _definition(
            tool_id="requests",
            display_name="requests",
            category="python_package",
            module_ids=("m16_ops_quality",),
            runtime="python",
            workspace_path="storage/workspaces/m16_ops_quality/tools/requests",
            expected_version="2.32.0",
            metadata={"python_package_name": "requests"},
        )
    )

    assert step.status == INSTALL_STATUS_READY
    assert step.manager == INSTALL_MANAGER_PIP
    assert step.command_argv == ("python", "-m", "pip", "install", "requests==2.32.0")


def test_docker_image_requires_image_metadata() -> None:
    missing = build_tool_install_step(_definition(category="docker_image", runtime="docker", metadata={}))
    ready = build_tool_install_step(_definition(category="docker_image", runtime="docker", metadata={"docker_image": "project/image:1"}))

    assert missing.status == INSTALL_STATUS_NEEDS_METADATA
    assert missing.manager == INSTALL_MANAGER_DOCKER
    assert ready.status == INSTALL_STATUS_READY
    assert ready.command_argv == ("docker", "pull", "project/image:1")


def test_external_service_and_hardware_are_not_local_install_commands() -> None:
    service = build_tool_install_step(_definition(category="cloud_api", runtime="api", metadata={}))
    hardware = build_tool_install_step(_definition(category="hardware", runtime="hardware", metadata={}))

    assert service.status == INSTALL_STATUS_EXTERNAL_SERVICE
    assert service.manager == INSTALL_MANAGER_NONE
    assert hardware.status == INSTALL_STATUS_HARDWARE_REQUIRED
    assert hardware.command_argv == ()


def test_module_install_plan_uses_registered_documented_tools_without_executing() -> None:
    plan = build_module_tool_install_plan("m01_osint")

    assert plan.module_id == "m01_osint"
    assert plan.count >= 20
    assert plan.execution_performed is False
    assert plan.needs_metadata_count >= 1
