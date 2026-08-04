"""Target-bound M01 OSINT operations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from app.core.m01_findings import M01Finding, derive_m01_passive_findings
from app.core.osint_domain_snapshot import DomainSnapshot, build_passive_domain_snapshot, normalize_domain
from app.core.target_model import TARGET_DOMAIN, TARGET_URL, TargetRecord
from app.core.target_workspace import bind_target_module_workspace

M01_MODULE_ID = "m01_osint"


@dataclass(frozen=True, slots=True)
class TargetPassiveDNSResult:
    """Passive DNS result bound to a concrete target workspace."""

    target_id: str
    module_id: str
    domain: str
    snapshot: DomainSnapshot
    artifact_path: Path
    report_path: Path
    findings_path: Path
    findings: tuple[M01Finding, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "target_id": self.target_id,
            "module_id": self.module_id,
            "domain": self.domain,
            "snapshot": self.snapshot.to_dict(),
            "artifact_path": self.artifact_path.as_posix(),
            "report_path": self.report_path.as_posix(),
            "findings_path": self.findings_path.as_posix(),
            "findings": [finding.to_dict() for finding in self.findings],
            "finding_count": len(self.findings),
            "execution_scope": "target_bound_passive_dns_only",
        }


@dataclass(frozen=True, slots=True)
class TargetPassiveDNSHistoryEntry:
    """Persisted M01 passive DNS run recovered from a target workspace."""

    domain: str
    artifact_path: Path
    report_path: Path | None
    findings_path: Path | None
    status: str
    checked_at: str | None
    finding_count: int
    external_source_count: int
    updated_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "domain": self.domain,
            "artifact_path": self.artifact_path.as_posix(),
            "report_path": self.report_path.as_posix() if self.report_path else None,
            "findings_path": self.findings_path.as_posix() if self.findings_path else None,
            "status": self.status,
            "checked_at": self.checked_at,
            "finding_count": self.finding_count,
            "external_source_count": self.external_source_count,
            "updated_at": self.updated_at,
        }


def domain_for_target(target: TargetRecord) -> str:
    """Return the domain usable for M01 passive DNS from a target record."""
    if target.target_type == TARGET_DOMAIN:
        return normalize_domain(target.normalized_value or target.value)
    if target.target_type == TARGET_URL:
        parsed = urlparse(target.normalized_value or target.value)
        hostname = parsed.hostname or ""
        return normalize_domain(hostname)
    raise ValueError("M01 passive DNS only supports domain and url targets.")


def _write_passive_dns_markdown_report(
    target: TargetRecord, result: DomainSnapshot, findings: tuple[M01Finding, ...], report_path: Path
) -> None:
    assessment = result.assessment
    notes = "\n".join(f"- {note}" for note in (assessment.exposure_notes if assessment else ("Sin lectura operativa",)))
    finding_rows = "\n".join(
        f"| {finding.finding_id} | {finding.severity} | {finding.title} | {finding.recommendation} |"
        for finding in findings
    )
    records = "\n".join(
        f"| {record.record_type} | {record.status} | {', '.join(record.values) if record.values else record.error or 'sin respuesta'} |"
        for record in result.records
    )
    external_sources = "\n".join(
        f"| {source.source} | {source.status} | {source.url} | {json.dumps(source.summary, ensure_ascii=False)} |"
        for source in result.external_sources
    )
    external_section = (
        "\n## External passive sources\n\n"
        "| Source | Status | URL | Summary |\n"
        "| --- | --- | --- | --- |\n"
        f"{external_sources}\n"
        if external_sources
        else ""
    )
    report = f"""# M01 Passive DNS Report

Target: `{target.target_id}`  
Name: `{target.name}`  
Domain: `{result.domain}`  
Status: `{result.status}`  
Checked at: `{result.checked_at}`

## Safety scope

- Passive DNS only: yes
- Port scan performed: no
- Web request to target performed: no
- Subdomain brute force performed: no

## Operational notes

{notes}

## Findings

| ID | Severity | Title | Recommendation |
| --- | --- | --- | --- |
{finding_rows}

## DNS records

| Type | Status | Values / error |
| --- | --- | --- |
{records}
{external_section}"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def list_target_passive_dns_history(
    target: TargetRecord, repo_root: Path | None = None, limit: int = 10
) -> tuple[TargetPassiveDNSHistoryEntry, ...]:
    """List persisted M01 passive DNS runs for a target from its workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    binding = bind_target_module_workspace(target, M01_MODULE_ID, repo_root=root)
    evidence_dir = binding.root_path / "evidence" / "passive_dns"
    if not evidence_dir.exists():
        return ()
    entries: list[TargetPassiveDNSHistoryEntry] = []
    for artifact_path in sorted(evidence_dir.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True):
        try:
            payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        domain = str(payload.get("domain") or artifact_path.stem.replace("_", "."))
        safe_name = domain.replace(".", "_")
        findings_path = binding.root_path / "findings" / "m01_passive_dns" / f"{safe_name}.json"
        report_path = binding.root_path / "reports" / "passive_dns" / f"{safe_name}.md"
        finding_count = 0
        if findings_path.exists():
            try:
                findings_payload = json.loads(findings_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                findings_payload = []
            if isinstance(findings_payload, list):
                finding_count = len(findings_payload)
        external_sources = payload.get("external_sources", [])
        entries.append(
            TargetPassiveDNSHistoryEntry(
                domain=domain,
                artifact_path=artifact_path,
                report_path=report_path if report_path.exists() else None,
                findings_path=findings_path if findings_path.exists() else None,
                status=str(payload.get("status", "UNKNOWN")),
                checked_at=str(payload.get("checked_at")) if payload.get("checked_at") else None,
                finding_count=finding_count,
                external_source_count=len(external_sources) if isinstance(external_sources, list) else 0,
                updated_at=datetime.fromtimestamp(artifact_path.stat().st_mtime, timezone.utc).isoformat(),
            )
        )
        if len(entries) >= limit:
            break
    return tuple(entries)


def run_target_passive_dns(
    target: TargetRecord, repo_root: Path | None = None, include_external: bool = False
) -> TargetPassiveDNSResult:
    """Run passive DNS for a target and write evidence into its M01 binding workspace."""
    root = Path.cwd() if repo_root is None else repo_root
    domain = domain_for_target(target)
    snapshot = build_passive_domain_snapshot(domain, include_external=include_external)
    binding = bind_target_module_workspace(target, M01_MODULE_ID, repo_root=root)
    evidence_dir = binding.root_path / "evidence" / "passive_dns"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    safe_name = domain.replace('.', '_')
    artifact_path = evidence_dir / f"{safe_name}.json"
    artifact_path.write_text(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    findings = derive_m01_passive_findings(snapshot)
    findings_dir = binding.root_path / "findings" / "m01_passive_dns"
    findings_dir.mkdir(parents=True, exist_ok=True)
    findings_path = findings_dir / f"{safe_name}.json"
    findings_path.write_text(
        json.dumps([finding.to_dict() for finding in findings], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path = binding.root_path / "reports" / "passive_dns" / f"{safe_name}.md"
    _write_passive_dns_markdown_report(target, snapshot, findings, report_path)
    return TargetPassiveDNSResult(
        target_id=target.target_id,
        module_id=M01_MODULE_ID,
        domain=domain,
        snapshot=snapshot,
        artifact_path=artifact_path,
        report_path=report_path,
        findings_path=findings_path,
        findings=findings,
    )
