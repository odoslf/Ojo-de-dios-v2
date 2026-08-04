"""Scoring engine foundation for technique result history."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from app.contracts.evidence_contract import (
    EVIDENCE_QUALITY_CRITICAL,
    EVIDENCE_QUALITY_HIGH,
    EVIDENCE_QUALITY_LOW,
    EVIDENCE_QUALITY_MEDIUM,
    EVIDENCE_QUALITY_NONE,
    RESULT_FAILED,
    RESULT_MANUAL_REQUIRED,
    RESULT_MISSING_TOOL,
    RESULT_PARTIAL,
    RESULT_SKIPPED,
    RESULT_SUCCESS,
    VALID_EVIDENCE_QUALITIES,
    VALID_RESULT_STATUSES,
)
from app.core.errors import ContractError
from app.db.repositories.scoring_repository import ScoringRepository

MIN_SCORE = 0.0
MAX_SCORE = 1.0
DEFAULT_SCORE = 0.0

DELTA_SUCCESS_HIGH = 0.20
DELTA_SUCCESS_MEDIUM = 0.12
DELTA_SUCCESS_LOW = 0.05
DELTA_PARTIAL = 0.04
DELTA_FAILED = -0.08
DELTA_MISSING_TOOL = -0.02
DELTA_MANUAL_REQUIRED = 0.0
DELTA_SKIPPED = 0.0


@dataclass
class ScoringEvent:
    """Technique result data accepted by the scoring engine."""

    target_id: str
    technique_id: str
    module_id: str
    run_id: str
    result_status: str
    evidence_quality: str
    evidence_ids: list[str] = field(default_factory=list)
    demo: bool = False
    real_execution: bool = True


@dataclass
class ScoringUpdate:
    """Calculated score update persisted to scoring history."""

    score_id: str
    target_id: str
    technique_id: str
    module_id: str
    run_id: str
    result_status: str
    evidence_quality: str
    evidence_ids: list[str]
    score_before: float
    score_after: float
    delta: float
    reason: str
    demo: bool
    real_execution: bool
    created_at: str


def clamp_score(value: float) -> float:
    """Keep a score within the supported score range."""
    return min(max(value, MIN_SCORE), MAX_SCORE)


def validate_scoring_event(event: ScoringEvent) -> None:
    """Validate the scoring event contract."""
    if not event.target_id:
        raise ContractError("Target id cannot be empty.")
    if not event.technique_id:
        raise ContractError("Technique id cannot be empty.")
    if not event.module_id:
        raise ContractError("Module id cannot be empty.")
    if not event.run_id:
        raise ContractError("Run id cannot be empty.")
    if event.result_status not in VALID_RESULT_STATUSES:
        raise ContractError("Invalid result status.")
    if event.evidence_quality not in VALID_EVIDENCE_QUALITIES:
        raise ContractError("Invalid evidence quality.")
    if event.demo and event.real_execution:
        raise ContractError("Demo result cannot be marked as real execution.")


class ScoringEngine:
    """Calculate and persist score changes after technique results."""

    def __init__(self, repository: ScoringRepository) -> None:
        self.repository = repository

    def update_after_result(self, event: ScoringEvent) -> ScoringUpdate:
        """Validate, calculate, persist, and return a score update."""
        validate_scoring_event(event)
        score_before = self.repository.get_latest_score(event.target_id, event.technique_id)
        delta, reason = self.calculate_delta(event)
        score_after = clamp_score(score_before + delta)
        update = ScoringUpdate(
            score_id=str(uuid4()),
            target_id=event.target_id,
            technique_id=event.technique_id,
            module_id=event.module_id,
            run_id=event.run_id,
            result_status=event.result_status,
            evidence_quality=event.evidence_quality,
            evidence_ids=list(event.evidence_ids),
            score_before=score_before,
            score_after=score_after,
            delta=delta,
            reason=reason,
            demo=event.demo,
            real_execution=event.real_execution,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self.repository.record_history(update)
        commit = getattr(self.repository.session, "commit", None)
        if callable(commit):
            commit()
        return update

    def calculate_delta(self, event: ScoringEvent) -> tuple[float, str]:
        """Calculate the score delta and reason for a valid scoring event."""
        if event.demo:
            return 0.0, "Demo result does not change score."
        if not event.real_execution:
            return 0.0, "Non-real execution does not change score."

        if event.result_status == RESULT_SUCCESS:
            if not event.evidence_ids:
                return 0.0, "Success without evidence does not increase score."
            if event.evidence_quality == EVIDENCE_QUALITY_NONE:
                return 0.0, "Success with no evidence quality does not increase score."
            if event.evidence_quality == EVIDENCE_QUALITY_LOW:
                return DELTA_SUCCESS_LOW, "Low quality evidence supports small score increase."
            if event.evidence_quality == EVIDENCE_QUALITY_MEDIUM:
                return DELTA_SUCCESS_MEDIUM, "Medium quality evidence supports score increase."
            if event.evidence_quality in {EVIDENCE_QUALITY_HIGH, EVIDENCE_QUALITY_CRITICAL}:
                return DELTA_SUCCESS_HIGH, "High quality evidence supports strong score increase."

        if event.result_status == RESULT_PARTIAL:
            if event.evidence_ids and event.evidence_quality != EVIDENCE_QUALITY_NONE:
                return DELTA_PARTIAL, "Partial result with evidence supports small score increase."
            return 0.0, "Partial result without evidence does not change score."

        if event.result_status == RESULT_FAILED:
            return DELTA_FAILED, "Failed result decreases score."

        if event.result_status == RESULT_MISSING_TOOL:
            return DELTA_MISSING_TOOL, "Missing tool slightly decreases readiness score."

        if event.result_status == RESULT_MANUAL_REQUIRED:
            return DELTA_MANUAL_REQUIRED, "Manual implementation required does not change score."

        if event.result_status == RESULT_SKIPPED:
            return DELTA_SKIPPED, "Skipped result does not change score."

        raise ContractError("Invalid result status.")
