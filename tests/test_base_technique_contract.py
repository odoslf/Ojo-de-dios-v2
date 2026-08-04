"""Base technique contract tests."""

import pytest

from app.contracts.evidence_contract import (
    EVIDENCE_QUALITY_LOW,
    EvidenceRecord,
    RESULT_MANUAL_REQUIRED,
)
from app.contracts.manual_required import ManualImplementationRequired
from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_IMPLEMENTACION_USUARIO_REQUERIDA,
    STATUS_READY_PASSIVE,
    TechniqueExecutionContext,
)
from app.core.errors import ContractError
from app.core.permission_levels import PERMISSION_PASSIVE


class DummyTechnique(BaseTechnique):
    technique_id = "test.dummy"
    module_id = "test"
    display_name = "Dummy"
    description = "Dummy technique"
    tool_name = "none"
    recommended_version = "none"
    runtime = "python"
    worker = "none"
    permission_level = PERMISSION_PASSIVE
    implementation_status = STATUS_IMPLEMENTACION_USUARIO_REQUERIDA
    requires_user_implementation = True


class ReadyButUserRequired(DummyTechnique):
    implementation_status = STATUS_READY_PASSIVE
    requires_user_implementation = True


class BadPermission(DummyTechnique):
    permission_level = "BAD_PERMISSION"


def test_base_technique_default_behaviors() -> None:
    technique = DummyTechnique()
    context = TechniqueExecutionContext(target_id="target-1", run_id="run-1", mode="demo")
    evidence = [
        EvidenceRecord(
            evidence_id="evidence-1",
            run_id="run-1",
            target_id="target-1",
            technique_id="test.dummy",
            module_id="test",
            evidence_type="text",
            quality=EVIDENCE_QUALITY_LOW,
            summary="summary",
        )
    ]

    technique.validate_metadata()
    assert technique.prepare(context) is context
    with pytest.raises(ManualImplementationRequired):
        technique.execute(context)
    parsed = technique.parse_result({"value": 1})
    assert parsed.result_status == RESULT_MANUAL_REQUIRED
    assert technique.score_result(evidence) == 0.0
    exported = technique.export_to_mano(evidence)
    assert exported["evidence_count"] == 1
    assert technique.get_permission_profile().technique_id == "test.dummy"


def test_ready_status_cannot_require_user_implementation() -> None:
    with pytest.raises(ContractError):
        ReadyButUserRequired().validate_metadata()


def test_bad_permission_fails_metadata_validation() -> None:
    with pytest.raises(ContractError):
        BadPermission().validate_metadata()
