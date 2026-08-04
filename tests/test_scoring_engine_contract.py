"""Scoring engine contract tests."""

import pytest
from sqlalchemy import create_engine

from app.contracts.evidence_contract import (
    EVIDENCE_QUALITY_HIGH,
    EVIDENCE_QUALITY_MEDIUM,
    EVIDENCE_QUALITY_NONE,
    RESULT_FAILED,
    RESULT_MANUAL_REQUIRED,
    RESULT_MISSING_TOOL,
    RESULT_SUCCESS,
)
from app.core.errors import ContractError
from app.core.scoring_engine import (
    DELTA_FAILED,
    DELTA_MANUAL_REQUIRED,
    DELTA_MISSING_TOOL,
    DELTA_SUCCESS_HIGH,
    MAX_SCORE,
    MIN_SCORE,
    ScoringEngine,
    ScoringEvent,
    clamp_score,
    validate_scoring_event,
)
from app.db.repositories.scoring_repository import ScoringRepository
from app.db.session import create_session_factory, init_db


def _session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'scoring-engine.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return session_factory()


def _engine(tmp_path) -> ScoringEngine:
    return ScoringEngine(ScoringRepository(_session(tmp_path)))


def _event(**overrides) -> ScoringEvent:
    data = {
        "target_id": "target-1",
        "technique_id": "technique-1",
        "module_id": "module-1",
        "run_id": "run-1",
        "result_status": RESULT_SUCCESS,
        "evidence_quality": EVIDENCE_QUALITY_HIGH,
        "evidence_ids": ["evidence-1"],
        "demo": False,
        "real_execution": True,
    }
    data.update(overrides)
    return ScoringEvent(**data)


def test_success_with_high_quality_evidence_increases_score(tmp_path) -> None:
    engine = _engine(tmp_path)

    update = engine.update_after_result(_event())

    assert update.score_before == 0.0
    assert update.delta == DELTA_SUCCESS_HIGH
    assert update.score_after == DELTA_SUCCESS_HIGH


def test_failed_result_decreases_existing_score(tmp_path) -> None:
    engine = _engine(tmp_path)
    engine.update_after_result(_event())

    update = engine.update_after_result(
        _event(run_id="run-2", result_status=RESULT_FAILED, evidence_quality=EVIDENCE_QUALITY_NONE, evidence_ids=[])
    )

    assert update.score_before == DELTA_SUCCESS_HIGH
    assert update.delta == DELTA_FAILED
    assert update.score_after == DELTA_SUCCESS_HIGH + DELTA_FAILED


def test_clamp_score_stays_within_bounds() -> None:
    assert clamp_score(-1.0) == MIN_SCORE
    assert clamp_score(2.0) == MAX_SCORE
    assert clamp_score(0.5) == 0.5


def test_manual_required_does_not_change_score(tmp_path) -> None:
    engine = _engine(tmp_path)

    update = engine.update_after_result(
        _event(result_status=RESULT_MANUAL_REQUIRED, evidence_quality=EVIDENCE_QUALITY_NONE, evidence_ids=[])
    )

    assert update.delta == DELTA_MANUAL_REQUIRED
    assert update.score_before == update.score_after


def test_missing_tool_slightly_decreases_score(tmp_path) -> None:
    engine = _engine(tmp_path)
    engine.update_after_result(_event())

    update = engine.update_after_result(
        _event(run_id="run-2", result_status=RESULT_MISSING_TOOL, evidence_quality=EVIDENCE_QUALITY_NONE, evidence_ids=[])
    )

    assert update.delta == DELTA_MISSING_TOOL
    assert update.score_after == DELTA_SUCCESS_HIGH + DELTA_MISSING_TOOL


def test_validate_scoring_event_rejects_invalid_result_status() -> None:
    with pytest.raises(ContractError):
        validate_scoring_event(_event(result_status="INVALID", evidence_quality=EVIDENCE_QUALITY_MEDIUM))


def test_validate_scoring_event_rejects_invalid_evidence_quality() -> None:
    with pytest.raises(ContractError):
        validate_scoring_event(_event(evidence_quality="invalid"))
