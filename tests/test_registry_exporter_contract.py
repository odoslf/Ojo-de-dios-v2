"""Technique registry exporter tests."""

import json

from app.contracts.technique_contract import BaseTechnique, STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.registry_exporter import (
    export_registry_json,
    export_registry_yaml,
    registry_metadata_to_json_text,
    registry_metadata_to_yaml_text,
)
from app.core.technique_registry import create_empty_registry


class DummyPassiveTechnique(BaseTechnique):
    technique_id = "test.passive"
    module_id = "test"
    display_name = "Passive Test"
    description = "Passive test technique"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True


def build_registry():
    registry = create_empty_registry()
    registry.register(DummyPassiveTechnique)
    return registry


def test_registry_metadata_to_json_text_is_valid_json() -> None:
    data = json.loads(registry_metadata_to_json_text(build_registry()))

    assert data[0]["technique_id"] == "test.passive"


def test_registry_metadata_to_yaml_text_is_stable_without_pyyaml() -> None:
    yaml_text = registry_metadata_to_yaml_text(build_registry())

    assert "- technique_id: test.passive" in yaml_text


def test_export_registry_json_and_yaml_write_files(tmp_path) -> None:
    registry = build_registry()
    json_path = export_registry_json(registry, tmp_path / "exports" / "registry.json")
    yaml_path = export_registry_yaml(registry, tmp_path / "exports" / "registry.yaml")

    assert json.loads(json_path.read_text(encoding="utf-8"))[0]["technique_id"] == "test.passive"
    assert "test.passive" in yaml_path.read_text(encoding="utf-8")
