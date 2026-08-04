"""Scoring tests for non-evidenced and demo results."""

import pytest
from sqlalchemy import create_engine

from app.contracts.evidence_contract import (
    EVIDENCE_QUALITY_HIGH,
    EVIDENCE_QUALITY_LOW,
    EVIDENCE_QUALITY_NONE,
    RESULT_PARTIAL,
    RESULT_SUCCESS,
)
from app.core.errors import ContractError
from app.core.scoring_engine import DELTA_PARTIAL, ScoringEngine, ScoringEvent
from app.db.repositories.scoring_repository import ScoringRepository
from app.db.session import create_session_factory, init_db


def _engine(tmp_path) -> ScoringEngine:
    engine = create_engine(f"sqlite:///{tmp_path / 'scoring-no-fake.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return ScoringEngine(ScoringRepository(session_factory()))


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


def test_success_without_evidence_ids_does_not_increase_score(tmp_path) -> None:
    engine = _engine(tmp_path)

    update = engine.update_after_result(_event(evidence_ids=[]))

    assert update.delta == 0.0
    assert update.score_after == 0.0


def test_success_with_none_evidence_quality_does_not_increase_score(tmp_path) -> None:
    engine = _engine(tmp_path)

    update = engine.update_after_result(_event(evidence_quality=EVIDENCE_QUALITY_NONE))

    assert update.delta == 0.0
    assert update.score_after == 0.0


def test_demo_non_real_execution_does_not_change_score(tmp_path) -> None:
    engine = _engine(tmp_path)

    update = engine.update_after_result(_event(demo=True, real_execution=False))

    assert update.delta == 0.0
    assert update.score_before == update.score_after


def test_demo_real_execution_raises_contract_error(tmp_path) -> None:
    engine = _engine(tmp_path)

    with pytest.raises(ContractError):
        engine.update_after_result(_event(demo=True, real_execution=True))


def test_partial_without_evidence_does_not_change_score(tmp_path) -> None:
    engine = _engine(tmp_path)

    update = engine.update_after_result(
        _event(result_status=RESULT_PARTIAL, evidence_quality=EVIDENCE_QUALITY_NONE, evidence_ids=[])
    )

    assert update.delta == 0.0
    assert update.score_after == 0.0


def test_partial_with_evidence_increases_score_slightly(tmp_path) -> None:
    engine = _engine(tmp_path)

    update = engine.update_after_result(
        _event(result_status=RESULT_PARTIAL, evidence_quality=EVIDENCE_QUALITY_LOW, evidence_ids=["evidence-1"])
    )

    assert update.delta == DELTA_PARTIAL
    assert update.score_after == DELTA_PARTIAL
