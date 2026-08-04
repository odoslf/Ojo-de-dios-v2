"""User and role repository for Ojo de Dios."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.password_hashing import hash_password, verify_password
from app.auth.roles import ALL_ROLES, ROLE_ADMIN, ROLE_DESCRIPTIONS
from app.db.models import Role, User


class UsersRepository:
    """Persistence operations for roles and users."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_role(self, name: str, description: str | None = None) -> Role:
        """Create and persist a role."""
        if not name:
            raise ValueError("Role name cannot be empty.")
        role = Role(name=name, description=description)
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def get_role_by_name(self, name: str) -> Role | None:
        """Return a role by name when it exists."""
        return self.session.scalar(select(Role).where(Role.name == name))

    def ensure_default_roles(self) -> list[Role]:
        """Ensure all official roles exist and return them."""
        roles: list[Role] = []
        for role_name in sorted(ALL_ROLES):
            role = self.get_role_by_name(role_name)
            if role is None:
                role = Role(name=role_name, description=ROLE_DESCRIPTIONS.get(role_name))
                self.session.add(role)
                self.session.flush()
            roles.append(role)
        self.session.commit()
        for role in roles:
            self.session.refresh(role)
        return roles

    def create_user(
        self,
        username: str,
        password: str,
        role_name: str,
        password_hash_iterations: int = 260000,
    ) -> User:
        """Create and persist a user assigned to an existing role."""
        if not username:
            raise ValueError("Username cannot be empty.")
        if not password:
            raise ValueError("Password cannot be empty.")
        role = self.get_role_by_name(role_name)
        if role is None:
            raise ValueError(f"Role '{role_name}' does not exist.")
        if self.get_user_by_username(username) is not None:
            raise ValueError(f"User '{username}' already exists.")
        user = User(
            username=username,
            password_hash=hash_password(password, iterations=password_hash_iterations),
            role=role,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> User | None:
        """Return a user by username when it exists."""
        return self.session.scalar(select(User).where(User.username == username))

    def verify_user_password(self, username: str, password: str) -> bool:
        """Verify a user's password by username."""
        user = self.get_user_by_username(username)
        if user is None:
            return False
        return verify_password(password, user.password_hash)

    def ensure_initial_admin(
        self,
        username: str,
        password: str,
        password_hash_iterations: int = 260000,
    ) -> User | None:
        """Create the initial admin only when a non-empty password is explicitly configured."""
        if not username:
            raise ValueError("Initial admin username cannot be empty.")
        existing_user = self.get_user_by_username(username)
        if existing_user is not None:
            return existing_user
        if not password:
            return None
        return self.create_user(
            username=username,
            password=password,
            role_name=ROLE_ADMIN,
            password_hash_iterations=password_hash_iterations,
        )
