"""Database session helpers for Ojo de Dios."""

from collections.abc import Generator
from pathlib import Path
from urllib.parse import unquote, urlparse

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db.base import Base
from app.db import models  # noqa: F401


def get_database_url() -> str:
    """Return the configured database URL."""
    return get_settings().database_url


def _ensure_sqlite_parent_directory(database_url: str) -> None:
    parsed = urlparse(database_url)
    if parsed.scheme != "sqlite" or database_url.endswith(":memory:"):
        return
    if database_url.startswith("sqlite:////"):
        database_path = Path(unquote(parsed.path))
    elif database_url.startswith("sqlite:///"):
        database_path = Path(unquote(database_url.removeprefix("sqlite:///")))
    else:
        return
    if str(database_path) in {"", ":memory:"}:
        return
    if not database_path.is_absolute():
        database_path = Path.cwd() / database_path
    database_path.parent.mkdir(parents=True, exist_ok=True)


def create_engine_from_url(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the provided or configured database URL."""
    resolved_database_url = database_url or get_database_url()
    _ensure_sqlite_parent_directory(resolved_database_url)
    connect_args = {"check_same_thread": False} if resolved_database_url.startswith("sqlite") else {}
    return create_engine(resolved_database_url, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a SQLAlchemy session factory bound to an engine."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db(engine: Engine | None = None) -> None:
    """Create all current database tables."""
    resolved_engine = engine or create_engine_from_url()
    Base.metadata.create_all(bind=resolved_engine)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session for request-style dependency usage."""
    engine = create_engine_from_url()
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        yield session
