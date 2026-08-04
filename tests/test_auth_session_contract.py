"""Authentication, session and role contract tests."""

from fastapi.testclient import TestClient
from sqlalchemy import inspect, select

from app.auth.permissions import PERMISSION_MANAGE_USERS, role_has_permission
from app.auth.roles import ROLE_ADMIN, ROLE_OPERATOR, ROLE_READONLY
from app.auth.session_manager import SESSION_COOKIE_NAME, authenticated_user_from_token, create_user_session, revoke_user_session
from app.db.models import UserSession
from app.db.repositories.users_repository import UsersRepository
from app.db.session import create_engine_from_url, create_session_factory, get_session, init_db
from app.main import create_app


def _session_factory(tmp_path):
    engine = create_engine_from_url(f"sqlite:///{tmp_path / 'auth.sqlite3'}")
    init_db(engine)
    return engine, create_session_factory(engine)


def test_auth_tables_roles_and_passwords_are_real(tmp_path) -> None:
    engine, session_factory = _session_factory(tmp_path)
    inspector = inspect(engine)

    assert "user_sessions" in inspector.get_table_names()
    with session_factory() as session:
        repository = UsersRepository(session)
        roles = repository.ensure_default_roles()
        user = repository.create_user("admin", "CorrectHorseBatteryStaple!", ROLE_ADMIN)

        assert {role.name for role in roles} >= {ROLE_ADMIN, ROLE_OPERATOR, ROLE_READONLY}
        assert user.password_hash != "CorrectHorseBatteryStaple!"
        assert repository.verify_user_password("admin", "CorrectHorseBatteryStaple!") is True
        assert repository.verify_user_password("admin", "wrong") is False
        assert role_has_permission(ROLE_ADMIN, PERMISSION_MANAGE_USERS) is True
        assert role_has_permission(ROLE_READONLY, PERMISSION_MANAGE_USERS) is False


def test_session_tokens_are_hashed_revocable_and_return_authenticated_user(tmp_path) -> None:
    _, session_factory = _session_factory(tmp_path)
    with session_factory() as session:
        repository = UsersRepository(session)
        repository.ensure_default_roles()
        user = repository.create_user("operator", "CorrectHorseBatteryStaple!", ROLE_OPERATOR)
        created = create_user_session(session, user, user_agent="pytest", ip_address="127.0.0.1")
        stored = session.scalar(select(UserSession))

        assert stored is not None
        assert stored.session_token_hash != created.token
        current = authenticated_user_from_token(session, created.token)
        assert current is not None
        assert current.username == "operator"
        assert current.role == ROLE_OPERATOR
        assert revoke_user_session(session, created.token) is True
        assert authenticated_user_from_token(session, created.token) is None


def test_auth_api_login_me_logout_and_role_guard(tmp_path) -> None:
    _, session_factory = _session_factory(tmp_path)
    with session_factory() as session:
        repository = UsersRepository(session)
        repository.ensure_default_roles()
        repository.create_user("admin", "CorrectHorseBatteryStaple!", ROLE_ADMIN)
        repository.create_user("viewer", "CorrectHorseBatteryStaple!", ROLE_READONLY)

    def override_session():
        with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)

    failed = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    login = client.post("/api/auth/login", json={"username": "admin", "password": "CorrectHorseBatteryStaple!"})
    me = client.get("/api/auth/me")
    created = client.post("/api/auth/users", json={"username": "operator", "password": "CorrectHorseBatteryStaple!", "role": "operator"})
    logout = client.post("/api/auth/logout")
    me_after_logout = client.get("/api/auth/me")

    assert failed.status_code == 401
    assert login.status_code == 200
    assert SESSION_COOKIE_NAME in login.cookies
    assert me.json()["authenticated"] is True
    assert me.json()["user"]["role"] == ROLE_ADMIN
    assert created.status_code == 200
    assert created.json()["user"]["role"] == ROLE_OPERATOR
    assert logout.status_code == 200
    assert me_after_logout.json()["authenticated"] is False

    readonly = TestClient(app)
    readonly.post("/api/auth/login", json={"username": "viewer", "password": "CorrectHorseBatteryStaple!"})
    forbidden = readonly.post("/api/auth/users", json={"username": "blocked", "password": "CorrectHorseBatteryStaple!", "role": "operator"})
    assert forbidden.status_code == 403


def test_login_page_renders_real_form() -> None:
    client = TestClient(create_app())

    response = client.get("/login")

    assert response.status_code == 200
    assert "Acceso a Ojo de Dios" in response.text
    assert "cookie HttpOnly" in response.text
