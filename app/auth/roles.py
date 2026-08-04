"""Application roles for Ojo de Dios."""

ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_READONLY = "readonly"
ROLE_LAB = "lab"

ALL_ROLES = {
    ROLE_ADMIN,
    ROLE_OPERATOR,
    ROLE_READONLY,
    ROLE_LAB,
}

ROLE_DESCRIPTIONS = {
    ROLE_ADMIN: "Full controlled administration",
    ROLE_OPERATOR: "Create targets and run allowed jobs",
    ROLE_READONLY: "View dashboard, reports and evidence",
    ROLE_LAB: "Use demo mode and Hermes lab proposals",
}


def is_valid_role(role: str) -> bool:
    """Return whether a role is one of the official roles."""
    return role in ALL_ROLES
