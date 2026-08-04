"""Authenticated user helpers for Ojo de Dios."""

from dataclasses import dataclass

from app.auth.permissions import role_has_permission


@dataclass(frozen=True)
class AuthenticatedUser:
    """Minimal authenticated user representation."""

    id: int
    username: str
    role: str
    is_active: bool


def user_can(user: AuthenticatedUser, permission: str) -> bool:
    """Return whether an active user has a permission through their role."""
    return user.is_active and role_has_permission(user.role, permission)
