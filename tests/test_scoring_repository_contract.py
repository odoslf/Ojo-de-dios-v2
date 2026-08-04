"""Scoring repository contract tests."""

from sqlalchemy import create_engine, inspect

from app.contracts.evidence_contract import EVIDENCE_QUALITY_HIGH, RESULT_SUCCESS
from app.core.scoring_engine import ScoringUpdate
from app.db.repositories.scoring_repository import ScoringRepository
from app.db.session import create_session_factory, init_db


def _session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'scoring-repository.db'}", connect_args={"check_same_thread": False})
    init_db(engine)
    session_factory = create_session_factory(engine)
    return engine, session_factory()


def _update(score_id: str, score_after: float, target_id: str = "target-1", technique_id: str = "technique-1") -> ScoringUpdate:
    return ScoringUpdate(
        score_id=score_id,
        target_id=target_id,
        technique_id=technique_id,
        module_id="module-1",
        run_id=f"run-{score_id}",
        result_status=RESULT_SUCCESS,
        evidence_quality=EVIDENCE_QUALITY_HIGH,
        evidence_ids=[f"evidence-{score_id}"],
        score_before=0.0,
        score_after=score_after,
        delta=score_after,
        reason="test update",
        demo=False,
        real_execution=True,
        created_at=f"2026-05-30T00:00:0{score_id}+00:00",
    )


def test_get_latest_score_returns_default_without_history(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = ScoringRepository(session)

    assert repository.get_latest_score("target-1", "technique-1") == 0.0


def test_record_history_persists_scoring_history(tmp_path) -> None:
    engine, session = _session(tmp_path)
    inspector = inspect(engine)
    assert "scoring_history" in inspector.get_table_names()
    repository = ScoringRepository(session)

    model = repository.record_history(_update("1", 0.2))
    session.commit()

    assert model.score_id == "1"
    assert model.score_after == 0.2


def test_get_latest_score_returns_newest_score_after(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = ScoringRepository(session)
    repository.record_history(_update("1", 0.2))
    repository.record_history(_update("2", 0.4))
    session.commit()

    assert repository.get_latest_score("target-1", "technique-1") == 0.4


def test_list_history_for_technique_returns_history(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = ScoringRepository(session)
    repository.record_history(_update("1", 0.2))
    repository.record_history(_update("2", 0.4))
    session.commit()

    history = repository.list_history_for_technique("target-1", "technique-1")

    assert [item.score_id for item in history] == ["2", "1"]


def test_list_history_for_target_returns_history(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = ScoringRepository(session)
    repository.record_history(_update("1", 0.2, target_id="target-1"))
    repository.record_history(_update("2", 0.4, target_id="target-1"))
    repository.record_history(_update("3", 0.6, target_id="target-2"))
    session.commit()

    history = repository.list_history_for_target("target-1")

    assert [item.score_id for item in history] == ["2", "1"]


def test_history_limit_is_bounded_to_maximum(tmp_path) -> None:
    _, session = _session(tmp_path)
    repository = ScoringRepository(session)
    for index in range(501):
        repository.record_history(
            ScoringUpdate(
                score_id=str(index),
                target_id="target-1",
                technique_id="technique-1",
                module_id="module-1",
                run_id=f"run-{index}",
                result_status=RESULT_SUCCESS,
                evidence_quality=EVIDENCE_QUALITY_HIGH,
                evidence_ids=[f"evidence-{index}"],
                score_before=0.0,
                score_after=0.1,
                delta=0.1,
                reason="test update",
                demo=False,
                real_execution=True,
                created_at=f"2026-05-30T00:{index // 60:02d}:{index % 60:02d}+00:00",
            )
        )
    session.commit()

    assert len(repository.list_history_for_target("target-1", limit=999)) == 500
    assert len(repository.list_history_for_target("target-1", limit=0)) == 1
