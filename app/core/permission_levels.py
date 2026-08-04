"""Transversal permission levels for Ojo de Dios."""

from dataclasses import dataclass

from app.core.errors import ContractError

PERMISSION_PASSIVE = "PERMISSION_PASSIVE"
PERMISSION_ACTIVE_LOW = "PERMISSION_ACTIVE_LOW"
PERMISSION_ACTIVE_SENSITIVE = "PERMISSION_ACTIVE_SENSITIVE"
PERMISSION_HARDWARE = "PERMISSION_HARDWARE"
PERMISSION_RF_TRANSMIT = "PERMISSION_RF_TRANSMIT"
PERMISSION_CREDENTIALS = "PERMISSION_CREDENTIALS"
PERMISSION_CLOUD_MUTATION = "PERMISSION_CLOUD_MUTATION"
PERMISSION_PERSISTENCE = "PERMISSION_PERSISTENCE"
PERMISSION_LAB_ONLY = "PERMISSION_LAB_ONLY"

VALID_PERMISSION_LEVELS = {
    PERMISSION_PASSIVE,
    PERMISSION_ACTIVE_LOW,
    PERMISSION_ACTIVE_SENSITIVE,
    PERMISSION_HARDWARE,
    PERMISSION_RF_TRANSMIT,
    PERMISSION_CREDENTIALS,
    PERMISSION_CLOUD_MUTATION,
    PERMISSION_PERSISTENCE,
    PERMISSION_LAB_ONLY,
}

CONFIRMATION_REQUIRED_PERMISSION_LEVELS = {
    PERMISSION_ACTIVE_SENSITIVE,
    PERMISSION_RF_TRANSMIT,
    PERMISSION_CREDENTIALS,
    PERMISSION_CLOUD_MUTATION,
    PERMISSION_PERSISTENCE,
}

BLOCKED_INVALID_PERMISSION = "INVALID_PERMISSION"
BLOCKED_INVALID_EXECUTION_MODE = "INVALID_EXECUTION_MODE"
BLOCKED_OUT_OF_SCOPE = "OUT_OF_SCOPE"
BLOCKED_HARDWARE_REQUIRED = "HARDWARE_REQUIRED"
BLOCKED_NETWORK_REQUIRED = "NETWORK_REQUIRED"
BLOCKED_MANUAL_REQUIRED = "MANUAL_REQUIRED"
BLOCKED_NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
BLOCKED_DEMO_NOT_SUPPORTED = "DEMO_NOT_SUPPORTED"
BLOCKED_DRY_RUN_NOT_SUPPORTED = "DRY_RUN_NOT_SUPPORTED"
BLOCKED_LAB_ONLY = "LAB_ONLY"


@dataclass(frozen=True)
class TechniquePermissionProfile:
    """Permission requirements for a future executable capability."""

    technique_id: str
    permission_level: str
    requires_confirmation: bool = False
    requires_allowlisted_target: bool = False
    requires_hardware: bool = False
    requires_network: bool = False
    requires_user_logic: bool = False
    can_run_in_demo: bool = True
    can_run_in_dry_run: bool = True


def is_valid_permission_level(permission_level: str) -> bool:
    """Return whether a permission level is official."""
    return permission_level in VALID_PERMISSION_LEVELS


def permission_level_requires_confirmation(permission_level: str) -> bool:
    """Return whether a permission level requires explicit confirmation."""
    return permission_level in CONFIRMATION_REQUIRED_PERMISSION_LEVELS


def validate_permission_profile(profile: TechniquePermissionProfile) -> None:
    """Validate a permission profile contract."""
    if not profile.technique_id:
        raise ContractError("Technique id cannot be empty.")
    if not is_valid_permission_level(profile.permission_level):
        raise ContractError("Invalid permission level.")
    if permission_level_requires_confirmation(profile.permission_level) and not profile.requires_confirmation:
        raise ContractError("Permission level requires confirmation.")
