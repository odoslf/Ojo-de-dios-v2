"""Repository for persisted version lock records."""

from datetime import datetime

from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.core.version_lock import (
    RUNTIME_CUSTOM,
    VersionLockEntry,
    create_locked_entry,
    create_missing_lock,
    create_needs_review_entry,
    validate_version_lock_entry,
)
from app.db.models import VersionLock, utc_now


def _bounded_limit(limit: int) -> int:
    return min(max(limit, 1), 1000)


def _locked_at_from_entry(entry: VersionLockEntry) -> datetime:
    if entry.locked_at is None:
        return utc_now()
    return datetime.fromisoformat(entry.locked_at)


class VersionLockRepository:
    """Persistence operations for version lock metadata."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_lock(self, entry: VersionLockEntry) -> VersionLock:
        """Validate and persist a version lock, updating existing tool ids."""
        validate_version_lock_entry(entry)
        model = self.get_by_tool_id(entry.tool_id)
        if model is None:
            model = VersionLock(tool_id=entry.tool_id)
            self.session.add(model)

        model.tool_name = entry.tool_name
        model.module_id = entry.module_id
        model.recommended_version = entry.recommended_version
        model.resolved_version = entry.resolved_version
        model.source_url = entry.source_url
        model.runtime = entry.runtime
        model.binary_hash = entry.binary_hash
        model.locked_at = _locked_at_from_entry(entry)
        model.status = entry.status
        self.session.flush()
        return model

    def get_by_tool_id(self, tool_id: str) -> VersionLock | None:
        """Return a version lock by stable tool id."""
        return self.session.query(VersionLock).filter(VersionLock.tool_id == tool_id).one_or_none()

    def list_by_module(self, module_id: str, limit: int = 100) -> list[VersionLock]:
        """Return version locks for a module ordered by tool name."""
        return (
            self.session.query(VersionLock)
            .filter(VersionLock.module_id == module_id)
            .order_by(asc(VersionLock.tool_name))
            .limit(_bounded_limit(limit))
            .all()
        )

    def list_all(self, limit: int = 500) -> list[VersionLock]:
        """Return all version locks ordered by module and tool name."""
        return (
            self.session.query(VersionLock)
            .order_by(asc(VersionLock.module_id), asc(VersionLock.tool_name))
            .limit(_bounded_limit(limit))
            .all()
        )

    def mark_missing(
        self,
        tool_id: str,
        tool_name: str,
        module_id: str,
        recommended_version: str,
        runtime: str,
        source_url: str = "",
    ) -> VersionLock:
        """Persist a missing version lock entry."""
        entry = create_missing_lock(
            tool_id=tool_id,
            tool_name=tool_name,
            module_id=module_id,
            recommended_version=recommended_version,
            runtime=runtime,
            source_url=source_url,
        )
        return self.upsert_lock(entry)

    def mark_needs_review(
        self,
        tool_id: str,
        tool_name: str,
        module_id: str,
        recommended_version: str,
        resolved_version: str = "",
        runtime: str = RUNTIME_CUSTOM,
        source_url: str = "",
        binary_hash: str = "",
    ) -> VersionLock:
        """Persist a needs-review version lock entry."""
        entry = create_needs_review_entry(
            tool_id=tool_id,
            tool_name=tool_name,
            module_id=module_id,
            recommended_version=recommended_version,
            resolved_version=resolved_version,
            runtime=runtime,
            source_url=source_url,
            binary_hash=binary_hash,
        )
        return self.upsert_lock(entry)

    def mark_locked(
        self,
        tool_id: str,
        tool_name: str,
        module_id: str,
        recommended_version: str,
        resolved_version: str,
        runtime: str,
        source_url: str = "",
        binary_hash: str = "",
    ) -> VersionLock:
        """Persist a locked version entry from explicit version metadata."""
        entry = create_locked_entry(
            tool_id=tool_id,
            tool_name=tool_name,
            module_id=module_id,
            recommended_version=recommended_version,
            resolved_version=resolved_version,
            runtime=runtime,
            source_url=source_url,
            binary_hash=binary_hash,
        )
        return self.upsert_lock(entry)
