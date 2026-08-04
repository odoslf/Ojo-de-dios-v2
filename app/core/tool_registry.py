"""Registry for validated tool definitions."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from app.core.errors import ContractError
from app.core.tool_definition import ToolDefinition, list_tool_definitions_for_module, load_tool_definitions, validate_tool_definition
from app.core.workspace import normalize_tool_id

ToolRegistryKey = tuple[str, str]


class ToolRegistry:
    """Registry keyed by (module_id, tool_id) so shared tools remain module-aware."""

    def __init__(self) -> None:
        self._definitions: dict[ToolRegistryKey, ToolDefinition] = {}

    def register(self, definition: ToolDefinition) -> None:
        """Validate and register one tool definition."""
        validate_tool_definition(definition)
        normalized_tool_id = normalize_tool_id(definition.tool_id)
        for module_id in definition.module_ids:
            key = (module_id, normalized_tool_id)
            if key in self._definitions:
                raise ContractError(f"Duplicate tool definition: {module_id}/{normalized_tool_id}.")
            module_definition = definition
            if definition.module_ids != (module_id,):
                module_definition = replace(definition, module_ids=(module_id,))
                validate_tool_definition(module_definition)
            self._definitions[key] = module_definition

    def register_many(self, definitions: list[ToolDefinition] | tuple[ToolDefinition, ...]) -> None:
        """Register multiple tool definitions."""
        for definition in definitions:
            self.register(definition)

    def get(self, module_id: str, tool_id: str) -> ToolDefinition | None:
        """Return a tool definition for a module/tool pair, if present."""
        return self._definitions.get((module_id, normalize_tool_id(tool_id)))

    def require(self, module_id: str, tool_id: str) -> ToolDefinition:
        """Return a tool definition or raise a contract error."""
        definition = self.get(module_id, tool_id)
        if definition is None:
            raise ContractError(f"Tool definition not registered: {module_id}/{normalize_tool_id(tool_id)}.")
        return definition

    def list_keys(self) -> list[str]:
        """Return stable registry keys as module_id/tool_id strings."""
        return [f"{module_id}/{tool_id}" for module_id, tool_id in sorted(self._definitions)]

    def list_all(self) -> list[ToolDefinition]:
        """Return all registered definitions sorted by module and tool id."""
        return [self._definitions[key] for key in sorted(self._definitions)]

    def list_by_module(self, module_id: str) -> list[ToolDefinition]:
        """Return registered definitions for one module."""
        return [definition for definition in self.list_all() if module_id in definition.module_ids]

    def list_by_tool_id(self, tool_id: str) -> list[ToolDefinition]:
        """Return all module-scoped definitions for one normalized tool id."""
        normalized_tool_id = normalize_tool_id(tool_id)
        return [definition for definition in self.list_all() if definition.tool_id == normalized_tool_id]

    def count(self) -> int:
        """Return registered module/tool definition count."""
        return len(self._definitions)

    def clear(self) -> None:
        """Remove all registered definitions."""
        self._definitions.clear()

    def to_metadata_list(self) -> list[dict[str, Any]]:
        """Return JSON-safe metadata for all registered tool definitions."""
        return [definition.to_dict() for definition in self.list_all()]


def create_empty_tool_registry() -> ToolRegistry:
    """Create an empty tool registry."""
    return ToolRegistry()


def load_tool_registry_from_definitions(definitions: tuple[ToolDefinition, ...] | list[ToolDefinition]) -> ToolRegistry:
    """Create a registry from validated tool definitions."""
    registry = create_empty_tool_registry()
    registry.register_many(definitions)
    return registry


def load_documented_tool_registry() -> ToolRegistry:
    """Create a registry from every documented tool definition."""
    return load_tool_registry_from_definitions(load_tool_definitions())


def load_module_tool_registry(module_id: str) -> ToolRegistry:
    """Create a registry for one module's documented tool definitions."""
    return load_tool_registry_from_definitions(list_tool_definitions_for_module(module_id))
