"""Registry implementation-status consistency tests."""

import pytest

from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    STATUS_READY_PASSIVE,
)
from app.core.errors import ContractError
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.technique_registry import create_empty_registry


class BadReadyTechnique(BaseTechnique):
    technique_id = "test.bad_ready"
    module_id = "test"
    display_name = "Bad Ready"
    description = "Bad Ready"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_READY_PASSIVE
    requires_user_implementation = True


class BadManualTechnique(BaseTechnique):
    technique_id = "test.bad_manual"
    module_id = "test"
    display_name = "Bad Manual"
    description = "Bad Manual"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = False


def test_ready_technique_cannot_require_user_implementation() -> None:
    registry = create_empty_registry()

    with pytest.raises(ContractError):
        registry.register(BadReadyTechnique)


def test_manual_required_technique_must_require_user_implementation() -> None:
    registry = create_empty_registry()

    with pytest.raises(ContractError):
        registry.register(BadManualTechnique)
