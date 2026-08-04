"""Minimal transversal policy evaluation for Ojo de Dios."""

from dataclasses import dataclass

from app.core.constants import (
    EXECUTION_MODE_CONTROLLED,
    EXECUTION_MODE_DEMO,
    EXECUTION_MODE_DRY_RUN,
    EXECUTION_MODE_EXPERT,
    VALID_EXECUTION_MODES,
)
from app.core.errors import ContractError
from app.core.permission_levels import (
    BLOCKED_DEMO_NOT_SUPPORTED,
    BLOCKED_DRY_RUN_NOT_SUPPORTED,
    BLOCKED_HARDWARE_REQUIRED,
    BLOCKED_INVALID_EXECUTION_MODE,
    BLOCKED_INVALID_PERMISSION,
    BLOCKED_LAB_ONLY,
    BLOCKED_MANUAL_REQUIRED,
    BLOCKED_NEEDS_CONFIRMATION,
    BLOCKED_NETWORK_REQUIRED,
    BLOCKED_OUT_OF_SCOPE,
    PERMISSION_LAB_ONLY,
    TechniquePermissionProfile,
    validate_permission_profile,
)


@dataclass(frozen=True)
class PolicyDecision:
    """Result of a policy evaluation."""

    allowed: bool
    reason: str
    blocked_reason: str | None = None
    requires_confirmation: bool = False


def evaluate_execution_permission(
    profile: TechniquePermissionProfile,
    execution_mode: str,
    confirmed: bool = False,
    allowlisted_target: bool = True,
    hardware_available: bool = True,
    network_available: bool = True,
    user_logic_available: bool = True,
) -> PolicyDecision:
    """Evaluate whether a permission profile can run in an execution mode."""
    if execution_mode not in VALID_EXECUTION_MODES:
        return PolicyDecision(False, "Invalid execution mode.", BLOCKED_INVALID_EXECUTION_MODE)

    try:
        validate_permission_profile(profile)
    except ContractError:
        return PolicyDecision(False, "Invalid permission profile.", BLOCKED_INVALID_PERMISSION)

    if execution_mode == EXECUTION_MODE_DEMO:
        if not profile.can_run_in_demo:
            return PolicyDecision(False, "Demo mode is not supported.", BLOCKED_DEMO_NOT_SUPPORTED)
        return PolicyDecision(True, "Execution allowed by policy.")

    if execution_mode == EXECUTION_MODE_DRY_RUN:
        if not profile.can_run_in_dry_run:
            return PolicyDecision(False, "Dry run mode is not supported.", BLOCKED_DRY_RUN_NOT_SUPPORTED)
        return PolicyDecision(True, "Execution allowed by policy.")

    if profile.permission_level == PERMISSION_LAB_ONLY and execution_mode in {
        EXECUTION_MODE_CONTROLLED,
        EXECUTION_MODE_EXPERT,
    }:
        return PolicyDecision(False, "Lab-only permission is not allowed in this mode.", BLOCKED_LAB_ONLY)

    if profile.requires_allowlisted_target and not allowlisted_target:
        return PolicyDecision(False, "Target is out of scope.", BLOCKED_OUT_OF_SCOPE)

    if profile.requires_hardware and not hardware_available:
        return PolicyDecision(False, "Required hardware is not available.", BLOCKED_HARDWARE_REQUIRED)

    if profile.requires_network and not network_available:
        return PolicyDecision(False, "Required network is not available.", BLOCKED_NETWORK_REQUIRED)

    if profile.requires_user_logic and not user_logic_available:
        return PolicyDecision(False, "Required user logic is not available.", BLOCKED_MANUAL_REQUIRED)

    if profile.requires_confirmation and not confirmed:
        return PolicyDecision(
            False,
            "Execution requires confirmation.",
            BLOCKED_NEEDS_CONFIRMATION,
            requires_confirmation=True,
        )

    return PolicyDecision(True, "Execution allowed by policy.")
