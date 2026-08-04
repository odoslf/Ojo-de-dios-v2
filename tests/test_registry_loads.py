"""Technique registry loading tests."""

import pytest

from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
)
from app.core.errors import ContractError
from app.core.permission_levels import PERMISSION_PASSIVE
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


class SecondDummyTechnique(BaseTechnique):
    technique_id = "test.second"
    module_id = "test"
    display_name = "Second Test"
    description = "Second test technique"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True


class DuplicateDummyTechnique(DummyPassiveTechnique):
    display_name = "Duplicate Passive Test"


def test_empty_registry_starts_empty() -> None:
    assert create_empty_registry().count() == 0


def test_register_get_and_require() -> None:
    registry = create_empty_registry()

    registry.register(DummyPassiveTechnique)

    assert registry.count() == 1
    assert registry.get("test.passive") is DummyPassiveTechnique
    assert registry.require("test.passive") is DummyPassiveTechnique
    with pytest.raises(ContractError):
        registry.require("missing")


def test_list_ids_and_list_by_module_are_sorted() -> None:
    registry = create_empty_registry()
    registry.register(SecondDummyTechnique)
    registry.register(DummyPassiveTechnique)

    assert registry.list_ids() == ["test.passive", "test.second"]
    assert registry.list_by_module("test") == [DummyPassiveTechnique, SecondDummyTechnique]


def test_duplicate_technique_id_fails() -> None:
    registry = create_empty_registry()
    registry.register(DummyPassiveTechnique)

    with pytest.raises(ContractError):
        registry.register(DuplicateDummyTechnique)
