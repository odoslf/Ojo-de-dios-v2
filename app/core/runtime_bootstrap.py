"""Runtime bootstrap helpers for local product startup.

The bootstrap creates only real product runtime infrastructure: configured
storage directories and database tables. It does not create demo data, fake
techniques, placeholder jobs, or synthetic evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

from app.config import Settings, get_settings
from app.db.repositories.users_repository import UsersRepository
from app.db.session import create_engine_from_url, create_session_factory, init_db


@dataclass(frozen=True, slots=True)
class RuntimePathStatus:
    """Filesystem status for one runtime path."""

    name: str
    path: str
    exists: bool
    is_dir: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "path": self.path,
            "exists": self.exists,
            "is_dir": self.is_dir,
        }


@dataclass(frozen=True, slots=True)
class RuntimeBootstrapStatus:
    """Status of runtime bootstrap infrastructure."""

    directories: tuple[RuntimePathStatus, ...]
    database_url: str
    database_path: str | None
    database_exists: bool | None
    database_initialized: bool
    roles_seeded: bool = False
    role_count: int = 0
    initial_admin_configured: bool = False
    initial_admin_created: bool = False
    initial_admin_exists: bool = False
    initial_admin_username: str | None = None

    @property
    def ready(self) -> bool:
        """Return whether runtime directories exist and DB initialization succeeded when requested."""
        return all(directory.exists and directory.is_dir for directory in self.directories) and self.database_initialized

    def to_dict(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "directories": [directory.to_dict() for directory in self.directories],
            "database_url": self.database_url,
            "database_path": self.database_path,
            "database_exists": self.database_exists,
            "database_initialized": self.database_initialized,
            "roles_seeded": self.roles_seeded,
            "role_count": self.role_count,
            "initial_admin_configured": self.initial_admin_configured,
            "initial_admin_created": self.initial_admin_created,
            "initial_admin_exists": self.initial_admin_exists,
            "initial_admin_username": self.initial_admin_username,
            "fake_data_created": False,
            "placeholder_techniques_created": False,
        }


def _repo_root(repo_root: Path | None = None) -> Path:
    return (Path.cwd() if repo_root is None else repo_root).resolve()


def _resolve_repo_relative(path_value: str, repo_root: Path | None = None) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path.resolve()
    return (_repo_root(repo_root) / path).resolve()


def runtime_directory_paths(settings: Settings | None = None, repo_root: Path | None = None) -> tuple[tuple[str, Path], ...]:
    """Return configured runtime directories with stable names."""
    resolved_settings = settings or get_settings()
    return (
        ("storage_root", _resolve_repo_relative(resolved_settings.storage_root, repo_root=repo_root)),
        ("runtime", _resolve_repo_relative(resolved_settings.runtime_storage_dir, repo_root=repo_root)),
        ("workspaces", _resolve_repo_relative(resolved_settings.workspaces_storage_dir, repo_root=repo_root)),
        ("evidence", _resolve_repo_relative(resolved_settings.evidence_storage_dir, repo_root=repo_root)),
        ("job_logs", _resolve_repo_relative(resolved_settings.job_logs_storage_dir, repo_root=repo_root)),
        ("reports", _resolve_repo_relative(resolved_settings.reports_storage_dir, repo_root=repo_root)),
        ("temp", _resolve_repo_relative(resolved_settings.temp_storage_dir, repo_root=repo_root)),
    )


def _status_for_paths(paths: tuple[tuple[str, Path], ...]) -> tuple[RuntimePathStatus, ...]:
    return tuple(
        RuntimePathStatus(
            name=name,
            path=path.as_posix(),
            exists=path.exists(),
            is_dir=path.is_dir(),
        )
        for name, path in paths
    )


def sqlite_database_path(database_url: str, repo_root: Path | None = None) -> Path | None:
    """Return the local SQLite path for file-backed SQLite URLs, otherwise None."""
    parsed = urlparse(database_url)
    if parsed.scheme != "sqlite" or database_url.endswith(":memory:"):
        return None
    if database_url.startswith("sqlite:////"):
        database_path = Path(unquote(parsed.path))
    elif database_url.startswith("sqlite:///"):
        database_path = Path(unquote(database_url.removeprefix("sqlite:///")))
    else:
        return None
    if str(database_path) in {"", ":memory:"}:
        return None
    if database_path.is_absolute():
        return database_path.resolve()
    return (_repo_root(repo_root) / database_path).resolve()


def collect_runtime_bootstrap_status(
    settings: Settings | None = None,
    repo_root: Path | None = None,
    database_initialized: bool = False,
    roles_seeded: bool = False,
    role_count: int = 0,
    initial_admin_configured: bool = False,
    initial_admin_created: bool = False,
    initial_admin_exists: bool = False,
    initial_admin_username: str | None = None,
) -> RuntimeBootstrapStatus:
    """Collect runtime bootstrap status without creating directories or tables."""
    resolved_settings = settings or get_settings()
    paths = runtime_directory_paths(resolved_settings, repo_root=repo_root)
    database_path = sqlite_database_path(resolved_settings.database_url, repo_root=repo_root)
    return RuntimeBootstrapStatus(
        directories=_status_for_paths(paths),
        database_url=resolved_settings.database_url,
        database_path=database_path.as_posix() if database_path else None,
        database_exists=database_path.exists() if database_path else None,
        database_initialized=database_initialized,
        roles_seeded=roles_seeded,
        role_count=role_count,
        initial_admin_configured=initial_admin_configured,
        initial_admin_created=initial_admin_created,
        initial_admin_exists=initial_admin_exists,
        initial_admin_username=initial_admin_username,
    )


def bootstrap_runtime(
    settings: Settings | None = None,
    repo_root: Path | None = None,
    initialize_database: bool = True,
) -> RuntimeBootstrapStatus:
    """Create configured runtime directories and initialize database tables."""
    resolved_settings = settings or get_settings()
    paths = runtime_directory_paths(resolved_settings, repo_root=repo_root)
    for _, path in paths:
        path.mkdir(parents=True, exist_ok=True)
    database_initialized = False
    roles_seeded = False
    role_count = 0
    initial_admin_configured = bool(resolved_settings.initial_admin_password)
    initial_admin_created = False
    initial_admin_exists = False
    if initialize_database:
        engine = create_engine_from_url(resolved_settings.database_url)
        init_db(engine)
        session_factory = create_session_factory(engine)
        with session_factory() as session:
            users_repository = UsersRepository(session)
            roles = users_repository.ensure_default_roles()
            roles_seeded = True
            role_count = len(roles)
            existing_admin = users_repository.get_user_by_username(resolved_settings.initial_admin_username)
            initial_admin = users_repository.ensure_initial_admin(
                username=resolved_settings.initial_admin_username,
                password=resolved_settings.initial_admin_password,
                password_hash_iterations=resolved_settings.password_hash_iterations,
            )
            initial_admin_created = existing_admin is None and initial_admin is not None
            initial_admin_exists = initial_admin is not None
        database_initialized = True
    return collect_runtime_bootstrap_status(
        resolved_settings,
        repo_root=repo_root,
        database_initialized=database_initialized,
        roles_seeded=roles_seeded,
        role_count=role_count,
        initial_admin_configured=initial_admin_configured,
        initial_admin_created=initial_admin_created,
        initial_admin_exists=initial_admin_exists,
        initial_admin_username=resolved_settings.initial_admin_username if initial_admin_exists else None,
    )
