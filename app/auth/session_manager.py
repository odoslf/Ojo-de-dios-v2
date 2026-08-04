"""Session management for real login/logout flows."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.users import AuthenticatedUser
from app.db.models import User, UserSession

SESSION_COOKIE_NAME = "ojo_session"
DEFAULT_SESSION_TTL_HOURS = 12


@dataclass(frozen=True, slots=True)
class CreatedSession:
    """Session token returned once to the client plus persisted metadata."""

    token: str
    expires_at: datetime


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def hash_session_token(token: str) -> str:
    """Hash a bearer session token before database storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_user_session(
    session: Session,
    user: User,
    *,
    ttl_hours: int = DEFAULT_SESSION_TTL_HOURS,
    user_agent: str = "",
    ip_address: str = "",
) -> CreatedSession:
    """Create and persist a new random session token for an active user."""
    if not user.is_active:
        raise ValueError("Cannot create a session for an inactive user.")
    token = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(hours=max(1, min(ttl_hours, 168)))
    model = UserSession(
        session_token_hash=hash_session_token(token),
        user_id=user.id,
        expires_at=expires_at,
        user_agent=user_agent[:500],
        ip_address=ip_address[:64],
    )
    session.add(model)
    session.commit()
    return CreatedSession(token=token, expires_at=expires_at)


def authenticated_user_from_token(session: Session, token: str | None) -> AuthenticatedUser | None:
    """Return the active authenticated user for a valid, unexpired session token."""
    if not token:
        return None
    token_hash = hash_session_token(token)
    statement = select(UserSession).where(UserSession.session_token_hash == token_hash)
    model = session.scalar(statement)
    now = utc_now()
    if model is None or model.revoked_at is not None or _as_aware_utc(model.expires_at) <= now:
        return None
    user = model.user
    if user is None or not user.is_active:
        return None
    return AuthenticatedUser(id=user.id, username=user.username, role=user.role.name, is_active=user.is_active)


def revoke_user_session(session: Session, token: str | None) -> bool:
    """Revoke one session token when it exists."""
    if not token:
        return False
    model = session.scalar(select(UserSession).where(UserSession.session_token_hash == hash_session_token(token)))
    if model is None or model.revoked_at is not None:
        return False
    model.revoked_at = utc_now()
    session.add(model)
    session.commit()
    return True
