"""Panel schema contracts for Ojo de Dios."""

from dataclasses import dataclass, field
from typing import Any

from app.core.errors import ContractError


@dataclass
class PanelField:
    """Field shown by a future technique panel."""

    name: str
    label: str
    field_type: str
    required: bool = False
    default: Any | None = None
    help_text: str = ""


@dataclass
class TechniquePanelSchema:
    """Panel schema for a future technique UI."""

    technique_id: str
    module_id: str
    fields: list[PanelField] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)


def validate_panel_schema(schema: TechniquePanelSchema) -> None:
    """Validate a technique panel schema contract."""
    if not schema.technique_id:
        raise ContractError("Technique id cannot be empty.")
    if not schema.module_id:
        raise ContractError("Module id cannot be empty.")
    for panel_field in schema.fields:
        if not panel_field.name:
            raise ContractError("Panel field name cannot be empty.")
        if not panel_field.label:
            raise ContractError("Panel field label cannot be empty.")
        if not panel_field.field_type:
            raise ContractError("Panel field type cannot be empty.")
