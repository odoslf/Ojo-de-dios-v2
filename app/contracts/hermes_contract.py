"""Hermes skill contract definitions for Ojo de Dios."""

from dataclasses import dataclass, field

from app.contracts.technique_contract import (
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    VALID_IMPLEMENTATION_STATUSES,
)
from app.core.errors import ContractError

HERMES_STATUS_DRAFT = "draft"
HERMES_STATUS_DESIGNED = "designed"
HERMES_STATUS_GENERATED = "generated"
HERMES_STATUS_TESTED = "tested"
HERMES_STATUS_REVIEW_REQUIRED = "review_required"
HERMES_STATUS_APPROVED_BY_USER = "approved_by_user"
HERMES_STATUS_PROMOTED = "promoted"
HERMES_STATUS_REJECTED = "rejected"
HERMES_STATUS_ARCHIVED = "archived"

VALID_HERMES_STATUSES = {
    HERMES_STATUS_DRAFT,
    HERMES_STATUS_DESIGNED,
    HERMES_STATUS_GENERATED,
    HERMES_STATUS_TESTED,
    HERMES_STATUS_REVIEW_REQUIRED,
    HERMES_STATUS_APPROVED_BY_USER,
    HERMES_STATUS_PROMOTED,
    HERMES_STATUS_REJECTED,
    HERMES_STATUS_ARCHIVED,
}


@dataclass
class HermesSkillContract:
    """Contract for a future Hermes-generated skill proposal."""

    skill_id: str
    name: str
    version: str
    module_id: str
    description: str
    allowed_inputs: list[str] = field(default_factory=list)
    allowed_outputs: list[str] = field(default_factory=list)
    required_permissions: list[str] = field(default_factory=list)
    risk_level: str = "low"
    created_by: str = ""
    created_at: str | None = None
    status: str = HERMES_STATUS_DRAFT
    implementation_status: str = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation: bool = True
    approval_required: bool = True
    promotion_allowed: bool = False


def validate_hermes_skill_contract(skill: HermesSkillContract) -> None:
    """Validate a Hermes skill contract without running Hermes functionality."""
    if not skill.skill_id:
        raise ContractError("Skill id cannot be empty.")
    if not skill.name:
        raise ContractError("Skill name cannot be empty.")
    if not skill.version:
        raise ContractError("Skill version cannot be empty.")
    if not skill.module_id:
        raise ContractError("Module id cannot be empty.")
    if skill.status not in VALID_HERMES_STATUSES:
        raise ContractError("Invalid Hermes status.")
    if skill.implementation_status not in VALID_IMPLEMENTATION_STATUSES:
        raise ContractError("Invalid implementation status.")
    if skill.status != HERMES_STATUS_APPROVED_BY_USER and skill.promotion_allowed:
        raise ContractError("Promotion is only allowed after user approval.")
    if skill.status == HERMES_STATUS_PROMOTED and skill.approval_required:
        raise ContractError("Cannot create a promoted contract directly.")
