"""Database session contract tests."""

from sqlalchemy import inspect, select

from app.db.models import User
from app.db.session import create_engine_from_url, create_session_factory, init_db


def test_init_db_creates_initial_tables_without_seed_admin(tmp_path) -> None:
    database_url = f"sqlite:///{tmp_path / 'ojo_de_dios_test.sqlite3'}"
    engine = create_engine_from_url(database_url)

    init_db(engine)

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    assert {"roles", "users", "settings", "audit_log"}.issubset(table_names)

    session_factory = create_session_factory(engine)
    with session_factory() as session:
        users_count = len(session.scalars(select(User)).all())

    assert users_count == 0
