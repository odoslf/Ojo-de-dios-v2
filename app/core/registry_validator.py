"""Technique registry validation helpers."""

import json

from app.contracts.technique_contract import STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
from app.core.errors import ContractError
from app.core.technique_registry import TechniqueRegistry


def validate_registry(registry: TechniqueRegistry) -> None:
    """Validate every technique registered in a registry without executing techniques."""
    if not isinstance(registry, TechniqueRegistry):
        raise ContractError("Expected TechniqueRegistry instance.")
    for technique_cls in registry.list_all():
        technique = technique_cls()
        technique.validate_metadata()
        if not technique.technique_id:
            raise ContractError("Technique id cannot be empty.")
        if not technique.module_id:
            raise ContractError("Module id cannot be empty.")
        if not technique.display_name:
            raise ContractError("Display name cannot be empty.")


def assert_no_stub_marked_functional(registry: TechniqueRegistry) -> None:
    """Validate implementation status consistency without judging names or categories."""
    if not isinstance(registry, TechniqueRegistry):
        raise ContractError("Expected TechniqueRegistry instance.")
    for technique_cls in registry.list_all():
        technique = technique_cls()
        if technique.implementation_status.startswith("READY") and technique.requires_user_implementation:
            raise ContractError("Ready technique cannot require user implementation.")
        if (
            technique.implementation_status == STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
            and not technique.requires_user_implementation
        ):
            raise ContractError("Manual-required technique must require user implementation.")


def validate_registry_can_export(registry: TechniqueRegistry) -> None:
    """Validate registry metadata can be JSON serialized without writing files."""
    metadata = registry.to_metadata_list()
    json.dumps(metadata)
