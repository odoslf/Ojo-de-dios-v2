"""Authentication API routes."""

from __future__ import annotations

import json

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_permission
from app.auth.permissions import PERMISSION_MANAGE_USERS
from app.auth.roles import ROLE_ADMIN, ROLE_OPERATOR, ROLE_READONLY
from app.auth.session_manager import SESSION_COOKIE_NAME, create_user_session, revoke_user_session
from app.auth.users import AuthenticatedUser
from app.config import get_settings
from app.db.repositories.audit_log_repository import AuditLogRepository
from app.db.repositories.users_repository import UsersRepository
from app.db.session import get_session

router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1, max_length=512)


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=8, max_length=512)
    role: str = Field(pattern="^(admin|operator|readonly)$")


def _user_payload(user: AuthenticatedUser | None) -> dict[str, object] | None:
    if user is None:
        return None
    return {"id": user.id, "username": user.username, "role": user.role, "is_active": user.is_active}


@router.post("/api/auth/login")
def login(payload: LoginRequest, request: Request, response: Response, session: Session = Depends(get_session)) -> dict[str, object]:
    """Authenticate username/password and issue an HttpOnly session cookie."""
    users = UsersRepository(session)
    user = users.get_user_by_username(payload.username)
    if user is None or not user.is_active or not users.verify_user_password(payload.username, payload.password):
        AuditLogRepository(session).record_event("auth.login_failed", "Login failed.", actor_username=payload.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")
    created = create_user_session(
        session,
        user,
        user_agent=request.headers.get("user-agent", ""),
        ip_address=request.client.host if request.client else "",
    )
    response.set_cookie(
        SESSION_COOKIE_NAME,
        created.token,
        httponly=True,
        samesite="strict",
        secure=False,
        expires=created.expires_at,
    )
    AuditLogRepository(session).record_event("auth.login_success", "Login succeeded.", actor_username=user.username)
    return {"authenticated": True, "user": {"id": user.id, "username": user.username, "role": user.role.name, "is_active": user.is_active}, "expires_at": created.expires_at.isoformat()}


@router.post("/api/auth/logout")
def logout(response: Response, ojo_session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME), session: Session = Depends(get_session)) -> dict[str, object]:
    """Revoke current session and clear the browser cookie."""
    revoked = revoke_user_session(session, ojo_session)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"logged_out": True, "revoked": revoked}


@router.get("/api/auth/me")
def me(current_user: AuthenticatedUser | None = Depends(get_current_user)) -> dict[str, object]:
    """Return the current authenticated user, or anonymous state."""
    return {"authenticated": current_user is not None, "user": _user_payload(current_user)}


@router.post("/api/auth/users")
def create_user(
    payload: CreateUserRequest,
    current_user: AuthenticatedUser = Depends(require_permission(PERMISSION_MANAGE_USERS)),
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Create an operator/admin/readonly user; admin role is required."""
    if payload.role not in {ROLE_ADMIN, ROLE_OPERATOR, ROLE_READONLY}:
        raise HTTPException(status_code=400, detail="Unsupported role.")
    repository = UsersRepository(session)
    repository.ensure_default_roles()
    try:
        user = repository.create_user(payload.username, payload.password, payload.role, get_settings().password_hash_iterations)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    AuditLogRepository(session).record_event(
        "auth.user_created",
        "User created.",
        actor_username=current_user.username,
        metadata_json=json.dumps({"username": user.username, "role": user.role.name}, ensure_ascii=False),
    )
    return {"user": {"id": user.id, "username": user.username, "role": user.role.name, "is_active": user.is_active}}
