"""Target HTML form helper contract tests."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.repositories.targets_repository import TargetsRepository
from app.db.session import init_db
from app.web.routes_targets_pages import _create_target_from_form, _parse_allowed_modules, _target_to_record


def test_parse_allowed_modules_from_html_form_value() -> None:
    assert _parse_allowed_modules("m01_osint, m04_web_intrusion,, m15_cloud ") == [
        "m01_osint",
        "m04_web_intrusion",
        "m15_cloud",
    ]


def test_create_target_from_form_persists_target_and_fingerprint() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    with session_factory() as session:
        repository = TargetsRepository(session)
        target = _create_target_from_form(
            repository=repository,
            name="Example",
            target_type="domain",
            value="HTTPS://Example.COM/path",
            mode="dry_run",
            allowed_modules="m01_osint,m04_web_intrusion",
            noise_profile="normal",
            evidence_profile="standard",
            require_confirmations=True,
        )
        fingerprint = repository.get_latest_fingerprint(target.target_id)
        record = _target_to_record(target)

        assert target.normalized_value == "example.com"
        assert fingerprint is not None
        assert record.allowed_modules == ["m01_osint", "m04_web_intrusion"]
        assert record.require_confirmations is True


def test_parse_allowed_modules_accepts_newline_separated_values() -> None:
    assert _parse_allowed_modules("m01_osint\nm09_scraping_intelligence, m15_cloud") == [
        "m01_osint",
        "m09_scraping_intelligence",
        "m15_cloud",
    ]
