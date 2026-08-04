"""Audit log repository for Ojo de Dios."""

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.secret_redaction import redact_json_text, redact_text
from app.db.models import AuditLog


class AuditLogRepository:
    """Persistence operations for audit log entries."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def record_event(
        self,
        event_type: str,
        message: str,
        actor_username: str | None = None,
        metadata_json: str | None = None,
    ) -> AuditLog:
        """Create and persist an audit log event."""
        if not event_type:
            raise ValueError("Event type cannot be empty.")
        if not message:
            raise ValueError("Message cannot be empty.")
        event = AuditLog(
            event_type=event_type,
            message=redact_text(message),
            actor_username=actor_username,
            metadata_json=redact_json_text(metadata_json),
        )
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_recent(self, limit: int = 50) -> list[AuditLog]:
        """Return recent audit events ordered by creation time descending."""
        bounded_limit = min(max(limit, 1), 500)
        statement = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(bounded_limit)
        return list(self.session.scalars(statement).all())
