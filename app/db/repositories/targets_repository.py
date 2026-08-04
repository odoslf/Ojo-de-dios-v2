"""Repository for target records and target fingerprints."""

import json
from uuid import uuid4

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.target_fingerprint import TargetFingerprint, build_target_fingerprint, normalize_target_value
from app.core.target_model import TargetRequest, validate_target_request
from app.db.models import Target, TargetFingerprintModel


class TargetsRepository:
    """Persistence operations for targets."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_target(self, request: TargetRequest, created_by: str | None = None) -> Target:
        """Validate and persist a target definition."""
        validate_target_request(request)
        target = Target(
            target_id=str(uuid4()),
            name=request.name.strip(),
            target_type=request.target_type,
            value=request.value,
            normalized_value=normalize_target_value(request.target_type, request.value),
            mode=request.mode,
            allowed_modules_json=json.dumps(request.allowed_modules),
            limits_json=json.dumps(request.limits),
            noise_profile=request.noise_profile,
            evidence_profile=request.evidence_profile,
            require_confirmations=request.require_confirmations,
            metadata_json=json.dumps(request.metadata),
            created_by=created_by,
        )
        self.session.add(target)
        self.session.commit()
        self.session.refresh(target)
        return target

    def get_by_target_id(self, target_id: str) -> Target | None:
        """Return a target by public target id."""
        return self.session.query(Target).filter(Target.target_id == target_id).one_or_none()

    def list_targets(self, limit: int = 50) -> list[Target]:
        """Return recent targets, newest first."""
        bounded_limit = min(max(limit, 1), 500)
        return self.session.query(Target).order_by(desc(Target.created_at)).limit(bounded_limit).all()

    def create_fingerprint(self, fingerprint: TargetFingerprint) -> TargetFingerprintModel:
        """Persist a target fingerprint."""
        model = TargetFingerprintModel(
            target_id=fingerprint.target_id,
            target_type=fingerprint.target_type,
            original_value=fingerprint.original_value,
            normalized_value=fingerprint.normalized_value,
            fingerprint_json=json.dumps(fingerprint.fingerprint),
            tags_json=json.dumps(fingerprint.tags),
            confidence=fingerprint.confidence,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model

    def get_latest_fingerprint(self, target_id: str) -> TargetFingerprintModel | None:
        """Return the newest fingerprint for a target."""
        return (
            self.session.query(TargetFingerprintModel)
            .filter(TargetFingerprintModel.target_id == target_id)
            .order_by(desc(TargetFingerprintModel.created_at), desc(TargetFingerprintModel.id))
            .first()
        )

    def refresh_fingerprint(self, target: Target) -> TargetFingerprintModel:
        """Build and persist a fresh deterministic fingerprint for a target."""
        return self.create_fingerprint(build_target_fingerprint(target.target_id, target.target_type, target.value))
