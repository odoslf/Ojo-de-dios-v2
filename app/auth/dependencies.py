"""FastAPI dependencies for authenticated users and role checks."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import role_has_permission
from app.auth.session_manager import SESSION_COOKIE_NAME, authenticated_user_from_token
from app.auth.users import AuthenticatedUser
from app.db.session import get_session


def get_current_user(
    ojo_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    session: Session = Depends(get_session),
) -> AuthenticatedUser | None:
    """Return current user or None for anonymous requests."""
    return authenticated_user_from_token(session, ojo_session)


def require_authenticated_user(current_user: AuthenticatedUser | None = Depends(get_current_user)) -> AuthenticatedUser:
    """Require a valid login session."""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return current_user


def require_permission(permission: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    """Build a dependency that requires one permission through the user's role."""
    def dependency(current_user: AuthenticatedUser = Depends(require_authenticated_user)) -> AuthenticatedUser:
        if not role_has_permission(current_user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role permissions.")
        return current_user

    return dependency
