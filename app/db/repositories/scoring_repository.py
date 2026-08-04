"""Repository for persisted scoring history."""

import json
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import ScoringHistory

if TYPE_CHECKING:
    from app.core.scoring_engine import ScoringUpdate


def _bounded_limit(limit: int) -> int:
    return min(max(limit, 1), 500)


def _created_at_from_update(update: "ScoringUpdate") -> datetime:
    return datetime.fromisoformat(update.created_at)


class ScoringRepository:
    """Persistence operations for score history records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_latest_score(self, target_id: str, technique_id: str) -> float:
        """Return the newest score for a target and technique, or the default score."""
        latest = (
            self.session.query(ScoringHistory)
            .filter(
                ScoringHistory.target_id == target_id,
                ScoringHistory.technique_id == technique_id,
            )
            .order_by(desc(ScoringHistory.created_at), desc(ScoringHistory.id))
            .first()
        )
        if latest is None:
            return 0.0
        return float(latest.score_after)

    def record_history(self, update: "ScoringUpdate") -> ScoringHistory:
        """Persist a calculated score update."""
        model = ScoringHistory(
            score_id=update.score_id,
            target_id=update.target_id,
            technique_id=update.technique_id,
            module_id=update.module_id,
            run_id=update.run_id,
            result_status=update.result_status,
            evidence_quality=update.evidence_quality,
            evidence_ids_json=json.dumps(update.evidence_ids),
            score_before=update.score_before,
            score_after=update.score_after,
            delta=update.delta,
            reason=update.reason,
            demo=update.demo,
            real_execution=update.real_execution,
            created_at=_created_at_from_update(update),
        )
        self.session.add(model)
        self.session.flush()
        return model

    def list_history_for_technique(
        self,
        target_id: str,
        technique_id: str,
        limit: int = 100,
    ) -> list[ScoringHistory]:
        """Return scoring history for a target and technique ordered newest first."""
        return (
            self.session.query(ScoringHistory)
            .filter(
                ScoringHistory.target_id == target_id,
                ScoringHistory.technique_id == technique_id,
            )
            .order_by(desc(ScoringHistory.created_at), desc(ScoringHistory.id))
            .limit(_bounded_limit(limit))
            .all()
        )

    def list_history_for_target(
        self,
        target_id: str,
        limit: int = 100,
    ) -> list[ScoringHistory]:
        """Return scoring history for a target ordered newest first."""
        return (
            self.session.query(ScoringHistory)
            .filter(ScoringHistory.target_id == target_id)
            .order_by(desc(ScoringHistory.created_at), desc(ScoringHistory.id))
            .limit(_bounded_limit(limit))
            .all()
        )
