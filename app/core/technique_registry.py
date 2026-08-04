"""Extensible technique registry for Ojo de Dios."""

import inspect
from copy import deepcopy
from typing import Any

from app.contracts.technique_contract import BaseTechnique
from app.core.errors import ContractError


class TechniqueRegistry:
    """Registry of validated technique classes."""

    def __init__(self) -> None:
        self._techniques: dict[str, type[BaseTechnique]] = {}

    def register(self, technique_cls: type[BaseTechnique]) -> None:
        """Validate and register a technique class."""
        if not inspect.isclass(technique_cls):
            raise ContractError("Technique registration requires a class.")
        if not issubclass(technique_cls, BaseTechnique):
            raise ContractError("Technique class must inherit from BaseTechnique.")
        if technique_cls is BaseTechnique:
            raise ContractError("BaseTechnique itself cannot be registered.")

        technique = technique_cls()
        technique.validate_metadata()
        if technique.technique_id in self._techniques:
            raise ContractError(f"Duplicate technique id: {technique.technique_id}.")
        self._techniques[technique.technique_id] = technique_cls

    def register_many(self, technique_classes: list[type[BaseTechnique]]) -> None:
        """Register multiple technique classes."""
        for technique_cls in technique_classes:
            self.register(technique_cls)

    def get(self, technique_id: str) -> type[BaseTechnique] | None:
        """Return a registered technique class by id, if present."""
        return self._techniques.get(technique_id)

    def require(self, technique_id: str) -> type[BaseTechnique]:
        """Return a registered technique class or raise a contract error."""
        technique_cls = self.get(technique_id)
        if technique_cls is None:
            raise ContractError(f"Technique not registered: {technique_id}.")
        return technique_cls

    def list_ids(self) -> list[str]:
        """Return registered technique ids sorted alphabetically."""
        return sorted(self._techniques)

    def list_all(self) -> list[type[BaseTechnique]]:
        """Return registered technique classes sorted by technique id."""
        return [self._techniques[technique_id] for technique_id in self.list_ids()]

    def list_by_module(self, module_id: str) -> list[type[BaseTechnique]]:
        """Return registered technique classes for a module sorted by technique id."""
        return [
            technique_cls
            for technique_cls in self.list_all()
            if technique_cls().module_id == module_id
        ]

    def count(self) -> int:
        """Return the number of registered techniques."""
        return len(self._techniques)

    def clear(self) -> None:
        """Remove all registered techniques."""
        self._techniques.clear()

    def to_metadata_list(self) -> list[dict[str, Any]]:
        """Return serializable metadata for all registered techniques."""
        metadata: list[dict[str, Any]] = []
        for technique_cls in self.list_all():
            technique = technique_cls()
            metadata.append(
                {
                    "technique_id": technique.technique_id,
                    "module_id": technique.module_id,
                    "display_name": technique.display_name,
                    "description": technique.description,
                    "tool_name": technique.tool_name,
                    "recommended_version": technique.recommended_version,
                    "runtime": technique.runtime,
                    "worker": technique.worker,
                    "permission_level": technique.permission_level,
                    "risk_level": technique.risk_level,
                    "noise_level": technique.noise_level,
                    "required_inputs": list(technique.required_inputs),
                    "optional_inputs": list(technique.optional_inputs),
                    "expected_evidence": list(technique.expected_evidence),
                    "input_schema": deepcopy(technique.input_schema),
                    "ai_fillable_inputs": list(technique.ai_fillable_inputs),
                    "panel_fields": deepcopy(technique.panel_fields),
                    "success_markers": list(technique.success_markers),
                    "failure_markers": list(technique.failure_markers),
                    "demo_behavior": deepcopy(technique.demo_behavior),
                    "dry_run_behavior": deepcopy(technique.dry_run_behavior),
                    "user_logic_hook": technique.user_logic_hook,
                    "requires_allowlisted_target": technique.requires_allowlisted_target,
                    "requires_network": technique.requires_network,
                    "configurable_parameters": deepcopy(technique.configurable_parameters),
                    "implementation_status": technique.implementation_status,
                    "requires_user_implementation": technique.requires_user_implementation,
                    "requires_confirmation": technique.requires_confirmation,
                    "requires_hardware": technique.requires_hardware,
                    "can_run_in_demo": technique.can_run_in_demo,
                    "can_run_in_dry_run": technique.can_run_in_dry_run,
                    "hermes_enabled": technique.hermes_enabled,
                    "mistral_assistant": technique.mistral_assistant,
                    "evidence_schema": deepcopy(technique.evidence_schema),
                    "version_lock_id": technique.version_lock_id,
                }
            )
        return metadata


def create_empty_registry() -> TechniqueRegistry:
    """Create an empty technique registry."""
    return TechniqueRegistry()
