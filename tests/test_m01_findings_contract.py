import json
from pathlib import Path

from app.core.m01_findings import derive_m01_passive_findings
from app.core.osint_domain_snapshot import DNSRecordSet, DomainAssessment, DomainSnapshot
from app.core.target_model import TARGET_DOMAIN, TARGET_MODE_DRY_RUN, TargetRecord
from app.core.target_osint import run_target_passive_dns


def _snapshot(**overrides):
    data = {
        "domain": "example.com",
        "addresses": ("93.184.216.34",),
        "canonical_name": "example.com",
        "status": "RESOLVED",
        "checked_at": "2026-07-15T00:00:00+00:00",
        "records": (
            DNSRecordSet("MX", ("10 mail.example.com.",), "RESOLVED"),
            DNSRecordSet("TXT", (), "NO_ANSWER"),
            DNSRecordSet("NS", ("ns1.example.com.",), "RESOLVED"),
        ),
        "assessment": DomainAssessment(
            has_ipv4=True,
            has_ipv6=False,
            has_nameservers=True,
            has_mail_exchange=True,
            has_spf=False,
            has_dmarc=False,
            exposure_notes=("Correo publicado por MX",),
        ),
    }
    data.update(overrides)
    return DomainSnapshot(**data)


def test_m01_findings_detect_mail_control_gaps():
    findings = derive_m01_passive_findings(_snapshot())
    titles = {finding.title for finding in findings}

    assert "Correo publicado sin SPF detectado" in titles
    assert "Correo publicado sin DMARC detectado" in titles
    assert all(finding.to_dict()["real_execution"] is True for finding in findings)
    assert all(finding.to_dict()["demo"] is False for finding in findings)


def test_m01_findings_include_baseline_when_no_prioritized_issue():
    findings = derive_m01_passive_findings(
        _snapshot(
            records=(
                DNSRecordSet("A", ("93.184.216.34",), "RESOLVED"),
                DNSRecordSet("NS", ("ns1.example.com.",), "RESOLVED"),
            ),
            assessment=DomainAssessment(
                has_ipv4=True,
                has_ipv6=False,
                has_nameservers=True,
                has_mail_exchange=False,
                has_spf=False,
                has_dmarc=False,
                exposure_notes=("IPv4 publicado",),
            ),
        )
    )

    assert findings[0].severity == "info"
    assert findings[0].finding_id.startswith("m01-")


def test_target_passive_dns_writes_findings(monkeypatch, tmp_path: Path):
    snapshot = _snapshot()
    monkeypatch.setattr("app.core.target_osint.build_passive_domain_snapshot", lambda domain, include_external=False: snapshot)
    target = TargetRecord(
        target_id="target-1",
        name="Example",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
    )

    result = run_target_passive_dns(target, repo_root=tmp_path)

    assert result.findings_path.exists()
    payload = json.loads(result.findings_path.read_text(encoding="utf-8"))
    assert payload[0]["finding_id"].startswith("m01-")
    assert result.to_dict()["finding_count"] == len(payload)
    assert "Findings" in result.report_path.read_text(encoding="utf-8")


def test_target_passive_dns_history_lists_persisted_runs(monkeypatch, tmp_path: Path):
    snapshot = _snapshot()
    monkeypatch.setattr("app.core.target_osint.build_passive_domain_snapshot", lambda domain, include_external=False: snapshot)
    target = TargetRecord(
        target_id="target-history",
        name="Example History",
        target_type=TARGET_DOMAIN,
        value="example.com",
        normalized_value="example.com",
        mode=TARGET_MODE_DRY_RUN,
    )
    run_target_passive_dns(target, repo_root=tmp_path)

    from app.core.target_osint import list_target_passive_dns_history

    history = list_target_passive_dns_history(target, repo_root=tmp_path)

    assert len(history) == 1
    payload = history[0].to_dict()
    assert payload["domain"] == "example.com"
    assert payload["finding_count"] >= 1
    assert payload["report_path"].endswith("example_com.md")
