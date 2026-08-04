"""Evidence and job contract tests."""

import pytest

from app.contracts.evidence_contract import (
    EVIDENCE_QUALITY_HIGH,
    RESULT_SUCCESS,
    EvidenceRecord,
    validate_evidence_record,
)
from app.contracts.job_contract import (
    JOB_MODE_DEMO,
    JOB_STATUS_SUCCESS,
    JobRequest,
    JobResult,
    validate_job_request,
    validate_job_result,
)
from app.core.errors import ContractError


def make_evidence_record(**overrides) -> EvidenceRecord:
    values = {
        "evidence_id": "evidence-1",
        "run_id": "run-1",
        "target_id": "target-1",
        "technique_id": "technique-1",
        "module_id": "module-1",
        "evidence_type": "text",
        "quality": EVIDENCE_QUALITY_HIGH,
        "summary": "summary",
    }
    values.update(overrides)
    return EvidenceRecord(**values)


def test_valid_evidence_record_passes_validation() -> None:
    validate_evidence_record(make_evidence_record())


def test_demo_evidence_cannot_be_real_execution() -> None:
    with pytest.raises(ContractError):
        validate_evidence_record(make_evidence_record(demo=True, real_execution=True))


def test_invalid_evidence_quality_fails_validation() -> None:
    with pytest.raises(ContractError):
        validate_evidence_record(make_evidence_record(quality="invalid"))


def test_valid_job_request_passes_validation() -> None:
    request = JobRequest(job_id="job-1", target_id="target-1", created_by="admin", mode=JOB_MODE_DEMO)

    validate_job_request(request)


def test_invalid_job_request_mode_fails_validation() -> None:
    request = JobRequest(job_id="job-1", target_id="target-1", created_by="admin", mode="invalid")

    with pytest.raises(ContractError):
        validate_job_request(request)


def test_valid_job_result_passes_validation() -> None:
    result = JobResult(job_id="job-1", status=JOB_STATUS_SUCCESS, result_status=RESULT_SUCCESS)

    validate_job_result(result)


def test_invalid_job_status_fails_validation() -> None:
    result = JobResult(job_id="job-1", status="invalid", result_status=RESULT_SUCCESS)

    with pytest.raises(ContractError):
        validate_job_result(result)


def test_invalid_job_result_status_fails_validation() -> None:
    result = JobResult(job_id="job-1", status=JOB_STATUS_SUCCESS, result_status="invalid")

    with pytest.raises(ContractError):
        validate_job_result(result)
