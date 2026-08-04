"""Technique extensibility contract tests."""

import pytest

from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
)
from app.core.errors import ContractError
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.technique_registry import TechniqueRegistry


class ExtensibleTechnique(BaseTechnique):
    technique_id = "test.extensible"
    module_id = "test"
    display_name = "Extensible Technique"
    description = "Extensible test"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True
    required_inputs = ["target"]
    optional_inputs = ["notes"]
    ai_fillable_inputs = ["notes"]
    input_schema = {"target": {"type": "string"}}
    panel_fields = [{"name": "target", "label": "Target", "type": "text"}]
    success_markers = ["success"]
    failure_markers = ["failed"]
    demo_behavior = {"fixture": "demo.json"}
    dry_run_behavior = {"validate_only": True}
    user_logic_hook = "execute"


class NetworkTechnique(ExtensibleTechnique):
    technique_id = "test.network"
    requires_allowlisted_target = True
    requires_network = True


def test_extensible_technique_metadata_is_valid() -> None:
    ExtensibleTechnique().validate_metadata()


def test_permission_profile_preserves_target_and_network_requirements() -> None:
    profile = NetworkTechnique().get_permission_profile()

    assert profile.requires_allowlisted_target is True
    assert profile.requires_network is True


def test_registry_exports_extensibility_metadata() -> None:
    registry = TechniqueRegistry()
    registry.register(ExtensibleTechnique)

    metadata = registry.to_metadata_list()[0]

    assert metadata["input_schema"] == {"target": {"type": "string"}}
    assert metadata["ai_fillable_inputs"] == ["notes"]
    assert metadata["panel_fields"] == [
        {"name": "target", "label": "Target", "type": "text"}
    ]
    assert metadata["success_markers"] == ["success"]
    assert metadata["failure_markers"] == ["failed"]
    assert metadata["demo_behavior"] == {"fixture": "demo.json"}
    assert metadata["dry_run_behavior"] == {"validate_only": True}
    assert metadata["user_logic_hook"] == "execute"
    assert metadata["requires_allowlisted_target"] is False
    assert metadata["requires_network"] is False


def test_panel_fields_must_be_list() -> None:
    class BadPanelFieldsTechnique(ExtensibleTechnique):
        panel_fields = {"name": "target"}

    with pytest.raises(ContractError):
        BadPanelFieldsTechnique().validate_metadata()


def test_input_schema_must_be_dict() -> None:
    class BadInputSchemaTechnique(ExtensibleTechnique):
        input_schema = ["target"]

    with pytest.raises(ContractError):
        BadInputSchemaTechnique().validate_metadata()
