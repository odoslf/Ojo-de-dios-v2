"""Users, roles and password contract tests."""

from app.auth.password_hashing import hash_password, verify_password
from app.auth.permissions import (
    PERMISSION_CREATE_TARGET,
    PERMISSION_MANAGE_USERS,
    PERMISSION_USE_DEMO,
    PERMISSION_VIEW_DASHBOARD,
    get_permissions_for_role,
    role_has_permission,
)
from app.auth.roles import ALL_ROLES, ROLE_ADMIN, ROLE_LAB, ROLE_OPERATOR, ROLE_READONLY, is_valid_role
from app.db.repositories.users_repository import UsersRepository
from app.db.session import create_engine_from_url, create_session_factory, init_db


def test_official_roles_are_valid() -> None:
    assert ALL_ROLES == {ROLE_ADMIN, ROLE_OPERATOR, ROLE_READONLY, ROLE_LAB}
    assert all(is_valid_role(role) for role in ALL_ROLES)
    assert not is_valid_role("unknown")


def test_permissions_by_role() -> None:
    assert role_has_permission(ROLE_ADMIN, PERMISSION_MANAGE_USERS)
    assert role_has_permission(ROLE_OPERATOR, PERMISSION_CREATE_TARGET)
    assert role_has_permission(ROLE_READONLY, PERMISSION_VIEW_DASHBOARD)
    assert role_has_permission(ROLE_LAB, PERMISSION_USE_DEMO)
    assert not role_has_permission(ROLE_READONLY, PERMISSION_CREATE_TARGET)
    assert PERMISSION_VIEW_DASHBOARD in get_permissions_for_role(ROLE_OPERATOR)


def test_password_hashing_and_verification() -> None:
    password = "safe-local-test-password"

    stored_hash = hash_password(password)

    assert stored_hash != password
    assert password not in stored_hash
    assert verify_password(password, stored_hash)
    assert not verify_password("wrong-password", stored_hash)
    assert not verify_password(password, "invalid-hash")


def test_users_repository_creates_roles_and_user_with_hash(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'users_roles_test.sqlite3'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        repository = UsersRepository(session)
        roles = repository.ensure_default_roles()
        user = repository.create_user("admin", "safe-local-test-password", ROLE_ADMIN)

        assert len(roles) == 4
        assert user.username == "admin"
        assert user.password_hash != "safe-local-test-password"
        assert repository.verify_user_password("admin", "safe-local-test-password")
        assert not repository.verify_user_password("admin", "wrong-password")


def test_users_repository_ensures_initial_admin_only_with_configured_password(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'initial_admin_test.sqlite3'}"
    engine = create_engine_from_url(database_url)
    init_db(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        repository = UsersRepository(session)
        repository.ensure_default_roles()
        skipped = repository.ensure_initial_admin("admin", "")
        created = repository.ensure_initial_admin("admin", "safe-local-test-password")
        repeated = repository.ensure_initial_admin("admin", "different-password")

        assert skipped is None
        assert created is not None
        assert repeated.id == created.id
        assert repository.verify_user_password("admin", "safe-local-test-password")
        assert not repository.verify_user_password("admin", "different-password")
