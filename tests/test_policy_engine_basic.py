"""Basic policy engine tests."""

from app.core.constants import (
    EXECUTION_MODE_CONTROLLED,
    EXECUTION_MODE_DEMO,
    EXECUTION_MODE_DRY_RUN,
)
from app.core.permission_levels import (
    BLOCKED_DEMO_NOT_SUPPORTED,
    BLOCKED_DRY_RUN_NOT_SUPPORTED,
    BLOCKED_HARDWARE_REQUIRED,
    BLOCKED_INVALID_EXECUTION_MODE,
    BLOCKED_LAB_ONLY,
    BLOCKED_MANUAL_REQUIRED,
    BLOCKED_NEEDS_CONFIRMATION,
    BLOCKED_NETWORK_REQUIRED,
    PERMISSION_ACTIVE_LOW,
    PERMISSION_ACTIVE_SENSITIVE,
    PERMISSION_LAB_ONLY,
    PERMISSION_PASSIVE,
    TechniquePermissionProfile,
)
from app.core.policy_engine import evaluate_execution_permission


def test_passive_permission_allowed_in_demo() -> None:
    profile = TechniquePermissionProfile("passive-demo", PERMISSION_PASSIVE)

    decision = evaluate_execution_permission(profile, EXECUTION_MODE_DEMO)

    assert decision.allowed is True


def test_active_low_permission_allowed_in_dry_run() -> None:
    profile = TechniquePermissionProfile("active-low-dry-run", PERMISSION_ACTIVE_LOW)

    decision = evaluate_execution_permission(profile, EXECUTION_MODE_DRY_RUN)

    assert decision.allowed is True


def test_demo_blocked_when_not_supported() -> None:
    profile = TechniquePermissionProfile(
        "no-demo",
        PERMISSION_PASSIVE,
        can_run_in_demo=False,
    )

    decision = evaluate_execution_permission(profile, EXECUTION_MODE_DEMO)

    assert decision.blocked_reason == BLOCKED_DEMO_NOT_SUPPORTED


def test_dry_run_blocked_when_not_supported() -> None:
    profile = TechniquePermissionProfile(
        "no-dry-run",
        PERMISSION_PASSIVE,
        can_run_in_dry_run=False,
    )

    decision = evaluate_execution_permission(profile, EXECUTION_MODE_DRY_RUN)

    assert decision.blocked_reason == BLOCKED_DRY_RUN_NOT_SUPPORTED


def test_hardware_required_blocks_in_controlled_when_unavailable() -> None:
    profile = TechniquePermissionProfile(
        "hardware-required",
        PERMISSION_ACTIVE_LOW,
        requires_hardware=True,
    )

    decision = evaluate_execution_permission(
        profile,
        EXECUTION_MODE_CONTROLLED,
        hardware_available=False,
    )

    assert decision.blocked_reason == BLOCKED_HARDWARE_REQUIRED


def test_network_required_blocks_in_controlled_when_unavailable() -> None:
    profile = TechniquePermissionProfile(
        "network-required",
        PERMISSION_ACTIVE_LOW,
        requires_network=True,
    )

    decision = evaluate_execution_permission(
        profile,
        EXECUTION_MODE_CONTROLLED,
        network_available=False,
    )

    assert decision.blocked_reason == BLOCKED_NETWORK_REQUIRED


def test_user_logic_required_blocks_in_controlled_when_unavailable() -> None:
    profile = TechniquePermissionProfile(
        "manual-required",
        PERMISSION_ACTIVE_LOW,
        requires_user_logic=True,
    )

    decision = evaluate_execution_permission(
        profile,
        EXECUTION_MODE_CONTROLLED,
        user_logic_available=False,
    )

    assert decision.blocked_reason == BLOCKED_MANUAL_REQUIRED


def test_confirmation_required_blocks_when_not_confirmed() -> None:
    profile = TechniquePermissionProfile(
        "confirmation-required",
        PERMISSION_ACTIVE_SENSITIVE,
        requires_confirmation=True,
    )

    decision = evaluate_execution_permission(profile, EXECUTION_MODE_CONTROLLED)

    assert decision.blocked_reason == BLOCKED_NEEDS_CONFIRMATION
    assert decision.requires_confirmation is True


def test_confirmation_required_allows_when_confirmed() -> None:
    profile = TechniquePermissionProfile(
        "confirmation-confirmed",
        PERMISSION_ACTIVE_SENSITIVE,
        requires_confirmation=True,
    )

    decision = evaluate_execution_permission(
        profile,
        EXECUTION_MODE_CONTROLLED,
        confirmed=True,
    )

    assert decision.allowed is True


def test_lab_only_blocks_in_controlled() -> None:
    profile = TechniquePermissionProfile("lab-only", PERMISSION_LAB_ONLY)

    decision = evaluate_execution_permission(profile, EXECUTION_MODE_CONTROLLED)

    assert decision.blocked_reason == BLOCKED_LAB_ONLY


def test_invalid_mode_blocks() -> None:
    profile = TechniquePermissionProfile("invalid-mode", PERMISSION_PASSIVE)

    decision = evaluate_execution_permission(profile, "invalid-mode")

    assert decision.blocked_reason == BLOCKED_INVALID_EXECUTION_MODE
