"""Base technique contract definitions for Ojo de Dios."""

from dataclasses import dataclass, field
from typing import Any

from app.contracts.evidence_contract import EvidenceRecord, RESULT_MANUAL_REQUIRED
from app.contracts.manual_required import ManualImplementationRequired
from app.core.errors import ContractError
from app.core.permission_levels import (
    PERMISSION_PASSIVE,
    TechniquePermissionProfile,
    is_valid_permission_level,
    permission_level_requires_confirmation,
    validate_permission_profile,
)

STATUS_READY_PASSIVE = "READY_PASSIVE"
STATUS_READY_LOCAL_AI = "READY_LOCAL_AI"
STATUS_READY_CONTROLLED = "READY_CONTROLLED"
STATUS_IMPLEMENTACION_USUARIO_REQUERIDA = "IMPLEMENTACION_USUARIO_REQUERIDA"
STATUS_HARDWARE_REQUIRED = "HARDWARE_REQUIRED"
STATUS_MISSING_TOOL = "MISSING_TOOL"
STATUS_DISABLED_BY_POLICY = "DISABLED_BY_POLICY"

VALID_IMPLEMENTATION_STATUSES = {
    STATUS_READY_PASSIVE,
    STATUS_READY_LOCAL_AI,
    STATUS_READY_CONTROLLED,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    STATUS_HARDWARE_REQUIRED,
    STATUS_MISSING_TOOL,
    STATUS_DISABLED_BY_POLICY,
}


@dataclass
class TechniqueExecutionContext:
    """Runtime context passed to a technique execution."""

    target_id: str
    run_id: str
    mode: str
    parameters: dict[str, Any] = field(default_factory=dict)
    evidence_ids: list[str] = field(default_factory=list)
    confirmed: bool = False
    demo: bool = False
    dry_run: bool = False


@dataclass
class TechniqueExecutionResult:
    """Result returned by a technique execution or parser."""

    technique_id: str
    module_id: str
    result_status: str
    summary: str = ""
    evidence: list[EvidenceRecord] = field(default_factory=list)
    raw_result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BaseTechnique:
    """Base contract for future technique implementations."""

    technique_id: str = ""
    module_id: str = ""
    display_name: str = ""
    description: str = ""
    tool_name: str = ""
    recommended_version: str = ""
    runtime: str = ""
    worker: str = ""
    permission_level: str = PERMISSION_PASSIVE
    risk_level: str = "low"
    noise_level: str = "low"
    required_inputs: list[str] = []
    optional_inputs: list[str] = []
    expected_evidence: list[str] = []
    input_schema: dict[str, Any] = {}
    ai_fillable_inputs: list[str] = []
    panel_fields: list[dict[str, Any]] = []
    success_markers: list[str] = []
    failure_markers: list[str] = []
    demo_behavior: dict[str, Any] = {}
    dry_run_behavior: dict[str, Any] = {}
    user_logic_hook: str | None = None
    requires_allowlisted_target: bool = False
    requires_network: bool = False
    configurable_parameters: dict[str, Any] = {}
    implementation_status: str = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation: bool = True
    requires_confirmation: bool = False
    requires_hardware: bool = False
    can_run_in_demo: bool = True
    can_run_in_dry_run: bool = True
    hermes_enabled: bool = True
    mistral_assistant: str | None = None
    evidence_schema: dict[str, Any] = {}
    version_lock_id: str | None = None

    def get_permission_profile(self) -> TechniquePermissionProfile:
        """Return the transversal permission profile for this technique."""
        profile = TechniquePermissionProfile(
            technique_id=self.technique_id,
            permission_level=self.permission_level,
            requires_confirmation=self.requires_confirmation,
            requires_allowlisted_target=self.requires_allowlisted_target,
            requires_hardware=self.requires_hardware,
            requires_network=self.requires_network,
            can_run_in_demo=self.can_run_in_demo,
            can_run_in_dry_run=self.can_run_in_dry_run,
        )
        validate_permission_profile(profile)
        return profile

    def prepare(self, context: TechniqueExecutionContext) -> TechniqueExecutionContext:
        """Return the execution context unchanged by default."""
        return context

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        """Require a private implementation by default."""
        raise ManualImplementationRequired(
            "IMPLEMENTACION_USUARIO_REQUERIDA: conecta aquí tu lógica privada para esta técnica."
        )

    def parse_result(self, raw_result: Any) -> TechniqueExecutionResult:
        """Return a manual-required result when no parser is implemented."""
        return TechniqueExecutionResult(
            technique_id=self.technique_id,
            module_id=self.module_id,
            result_status=RESULT_MANUAL_REQUIRED,
            summary="No parser implemented for this technique.",
            raw_result={"raw": raw_result},
        )

    def score_result(self, evidence: list[EvidenceRecord]) -> float:
        """Return the default score for unimplemented scoring."""
        return 0.0

    def export_to_mano(self, evidence: list[EvidenceRecord]) -> dict[str, Any]:
        """Export a minimal MANO-compatible summary."""
        return {
            "technique_id": self.technique_id,
            "module_id": self.module_id,
            "evidence_count": len(evidence),
        }

    def validate_metadata(self) -> None:
        """Validate technique metadata."""
        if not self.technique_id:
            raise ContractError("Technique id cannot be empty.")
        if not self.module_id:
            raise ContractError("Module id cannot be empty.")
        if not self.display_name:
            raise ContractError("Display name cannot be empty.")
        if self.implementation_status not in VALID_IMPLEMENTATION_STATUSES:
            raise ContractError("Invalid implementation status.")
        if not is_valid_permission_level(self.permission_level):
            raise ContractError("Invalid permission level.")
        if (
            self.implementation_status == STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
            and not self.requires_user_implementation
        ):
            raise ContractError("Manual implementation status requires user implementation.")
        if self.implementation_status.startswith("READY") and self.requires_user_implementation:
            raise ContractError("Ready implementations cannot require user implementation.")
        metadata_types: tuple[tuple[str, type[Any]], ...] = (
            ("required_inputs", list),
            ("optional_inputs", list),
            ("expected_evidence", list),
            ("ai_fillable_inputs", list),
            ("panel_fields", list),
            ("success_markers", list),
            ("failure_markers", list),
            ("configurable_parameters", dict),
            ("evidence_schema", dict),
            ("input_schema", dict),
            ("demo_behavior", dict),
            ("dry_run_behavior", dict),
            ("requires_allowlisted_target", bool),
            ("requires_network", bool),
        )
        for field_name, expected_type in metadata_types:
            if not isinstance(getattr(self, field_name), expected_type):
                raise ContractError(f"{field_name} must be {expected_type.__name__}.")
        if self.user_logic_hook is not None and not isinstance(self.user_logic_hook, str):
            raise ContractError("user_logic_hook must be str or None.")
        if permission_level_requires_confirmation(self.permission_level) and not self.requires_confirmation:
            raise ContractError("Permission level requires confirmation.")
        self.get_permission_profile()
