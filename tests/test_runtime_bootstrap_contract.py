"""Runtime bootstrap contract tests."""

from pathlib import Path

from app.config import Settings
from app.core.runtime_bootstrap import bootstrap_runtime, collect_runtime_bootstrap_status, sqlite_database_path


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        database_url=f"sqlite:///{tmp_path / 'storage' / 'runtime' / 'ojo.sqlite3'}",
        storage_root="storage",
        runtime_storage_dir="storage/runtime",
        workspaces_storage_dir="storage/workspaces",
        evidence_storage_dir="storage/evidence",
        job_logs_storage_dir="storage/job_logs",
        reports_storage_dir="storage/reports",
        temp_storage_dir="storage/tmp",
    )


def test_bootstrap_runtime_creates_real_directories_and_sqlite_tables(tmp_path: Path) -> None:
    settings = _settings(tmp_path)

    before = collect_runtime_bootstrap_status(settings, repo_root=tmp_path)
    result = bootstrap_runtime(settings, repo_root=tmp_path)

    assert before.ready is False
    assert result.ready is True
    assert result.database_initialized is True
    assert result.database_exists is True
    assert result.roles_seeded is True
    assert result.role_count == 4
    assert result.initial_admin_configured is False
    assert result.initial_admin_created is False
    assert result.initial_admin_exists is False
    assert result.to_dict()["fake_data_created"] is False
    assert result.to_dict()["placeholder_techniques_created"] is False
    for directory in result.directories:
        assert Path(directory.path).is_dir()


def test_sqlite_database_path_resolves_repo_relative_file_url(tmp_path: Path) -> None:
    path = sqlite_database_path("sqlite:///storage/runtime/app.sqlite3", repo_root=tmp_path)

    assert path == (tmp_path / "storage" / "runtime" / "app.sqlite3").resolve()


def test_bootstrap_runtime_creates_initial_admin_when_password_is_configured(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite:///{tmp_path / 'storage' / 'runtime' / 'ojo-admin.sqlite3'}",
        initial_admin_username="admin",
        initial_admin_password="safe-local-test-password",
        storage_root="storage",
        runtime_storage_dir="storage/runtime",
        workspaces_storage_dir="storage/workspaces",
        evidence_storage_dir="storage/evidence",
        job_logs_storage_dir="storage/job_logs",
        reports_storage_dir="storage/reports",
        temp_storage_dir="storage/tmp",
    )

    result = bootstrap_runtime(settings, repo_root=tmp_path)

    assert result.initial_admin_configured is True
    assert result.initial_admin_created is True
    assert result.initial_admin_exists is True
    assert result.initial_admin_username == "admin"


def test_bootstrap_runtime_reports_existing_initial_admin_without_recreating(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite:///{tmp_path / 'storage' / 'runtime' / 'ojo-admin-existing.sqlite3'}",
        initial_admin_username="admin",
        initial_admin_password="safe-local-test-password",
        storage_root="storage",
        runtime_storage_dir="storage/runtime",
        workspaces_storage_dir="storage/workspaces",
        evidence_storage_dir="storage/evidence",
        job_logs_storage_dir="storage/job_logs",
        reports_storage_dir="storage/reports",
        temp_storage_dir="storage/tmp",
    )

    first = bootstrap_runtime(settings, repo_root=tmp_path)
    second = bootstrap_runtime(settings, repo_root=tmp_path)

    assert first.initial_admin_created is True
    assert second.initial_admin_created is False
    assert second.initial_admin_exists is True
