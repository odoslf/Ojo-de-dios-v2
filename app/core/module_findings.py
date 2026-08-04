"""Evidence-derived findings for target-scoped module artifacts."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TargetModuleFinding:
    """One deterministic finding derived only from persisted module evidence."""

    finding_id: str
    module_id: str
    severity: str
    title: str
    description: str
    recommendation: str
    evidence_refs: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe finding."""
        return {
            "finding_id": self.finding_id,
            "module_id": self.module_id,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "evidence_refs": list(self.evidence_refs),
        }


def _finding(
    module_id: str,
    severity: str,
    title: str,
    description: str,
    recommendation: str,
    evidence_refs: tuple[str, ...] = (),
) -> TargetModuleFinding:
    identity = "|".join((module_id, severity, title, description, *evidence_refs))
    return TargetModuleFinding(
        finding_id=hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16],
        module_id=module_id,
        severity=severity,
        title=title,
        description=description,
        recommendation=recommendation,
        evidence_refs=evidence_refs,
    )


def _list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def derive_target_module_findings(module_id: str, payload: dict[str, Any] | None) -> tuple[TargetModuleFinding, ...]:
    """Derive honest findings from stored module evidence without inventing external facts."""
    if not isinstance(payload, dict):
        return ()
    findings: list[TargetModuleFinding] = []
    if module_id == "m02_vulnerabilities":
        for service in _list(payload.get("services")):
            item = _dict(service)
            product = str(item.get("product") or "service")
            version = str(item.get("version") or "").strip()
            candidates = _list(item.get("nvd_candidates"))
            ref = tuple(str(item[key]) for key in ("evidence_ref", "port") if item.get(key))
            if candidates:
                findings.append(_finding(
                    module_id,
                    "high",
                    f"{product} has public CVE candidates",
                    f"{len(candidates)} public advisory candidate(s) were attached to the supplied {product} {version} observation.",
                    "Validate exact product, version, configuration and exposure before prioritising remediation.",
                    ref,
                ))
            if not version:
                findings.append(_finding(
                    module_id,
                    "medium",
                    f"{product} version is missing",
                    "The supplied service inventory lacks a concrete version for this service.",
                    "Collect or import a versioned observation so vulnerability mapping can be precise.",
                    ref,
                ))
    elif module_id == "m03_network_services":
        for service in _list(payload.get("services")):
            item = _dict(service)
            family = str(item.get("service_family") or "")
            product = str(item.get("product") or "service")
            if family in {"remote_access", "database"}:
                findings.append(_finding(
                    module_id,
                    "medium",
                    f"{family.replace('_', ' ').title()} service mapped",
                    f"{product} is classified as {family} from persisted service evidence.",
                    "Confirm business need, exposure path and access controls before selecting a follow-up technique.",
                    tuple(str(item[key]) for key in ("evidence_ref", "port") if item.get(key)),
                ))
    elif module_id == "m04_web_intrusion":
        posture = _dict(payload.get("posture"))
        missing = _list(posture.get("missing_or_unobserved"))
        if missing:
            findings.append(_finding(
                module_id,
                "medium",
                "Web baseline is missing expected defensive headers",
                "The supplied response metadata lacks or did not observe: " + ", ".join(str(item) for item in missing),
                "Validate application context and add the missing headers where applicable.",
                (str(payload.get("url") or ""),),
            ))
        status_code = int(payload.get("observation", {}).get("status_code", 0)) if isinstance(payload.get("observation"), dict) else 0
        if status_code >= 500:
            findings.append(_finding(module_id, "medium", "Server error observed", f"Observed HTTP {status_code}.", "Review server logs and reproduce through an approved workflow.", (str(payload.get("url") or ""),)))
    elif module_id == "m05_credentials":
        evidence = _dict(payload.get("evidence"))
        if evidence.get("fingerprint_sha256"):
            findings.append(_finding(
                module_id,
                "medium",
                "Credential material fingerprint recorded",
                "A credential-like artifact was fingerprinted and can be locally verified against its receipt.",
                "Verify ownership, rotation status and whether the credential should be revoked or scoped down.",
                (str(payload.get("receipt_id") or ""),),
            ))
    elif module_id == "m06_mitm_network":
        inspection = _dict(payload.get("inspection"))
        if inspection.get("format") == "unknown":
            findings.append(_finding(module_id, "low", "Capture format is unknown", "The uploaded capture header was not recognised.", "Re-import a PCAP/PCAPNG capture or attach tool metadata.", (str(payload.get("filename") or ""),)))
    elif module_id == "m07_post_exploitation":
        evidence = _dict(payload.get("evidence"))
        privilege = str(evidence.get("privilege_level") or "").casefold()
        if privilege in {"root", "administrator", "admin", "system"}:
            findings.append(_finding(module_id, "high", "Privileged session evidence", f"Stored session metadata indicates privilege level: {privilege}.", "Prioritise containment, credential review and evidence preservation.", (str(evidence.get("session_reference") or ""),)))
    elif module_id == "m08_dos_resilience":
        summary = _dict(payload.get("summary"))
        if isinstance(summary.get("availability_rate"), (int, float)) and float(summary["availability_rate"]) < 0.99:
            findings.append(_finding(module_id, "medium", "Availability sample below 99%", f"Supplied measurements show availability rate {summary['availability_rate']}.", "Review monitoring window, affected components and capacity signals.", (str(summary.get("sample_count") or ""),)))
        if isinstance(summary.get("latency_ms_max"), (int, float)) and float(summary["latency_ms_max"]) > 1000:
            findings.append(_finding(module_id, "low", "High latency sample observed", f"Maximum supplied latency was {summary['latency_ms_max']} ms.", "Correlate latency with infrastructure telemetry and upstream dependencies.", (str(summary.get("sample_count") or ""),)))
    elif module_id == "m09_scraping_intelligence":
        records = _list(payload.get("records"))
        if records:
            sources = {str(_dict(item).get("source") or "") for item in records}
            if len(sources) <= 1:
                findings.append(_finding(module_id, "low", "Low source diversity in intelligence dataset", "The imported dataset is based on a single source label.", "Add corroborating sources before making high-confidence decisions.", tuple(sorted(sources))))
    elif module_id == "m10_wireless_rf":
        observations = _list(payload.get("observations"))
        if observations:
            findings.append(_finding(module_id, "info", "Radio observations imported", f"{len(observations)} passive RF observation(s) were recorded.", "Correlate with site survey and authorised spectrum evidence.", (str(len(observations)),)))
    elif module_id == "m11_iot_physical":
        devices = _list(payload.get("devices"))
        unknown = [item for item in devices if str(_dict(item).get("owner") or "unknown").casefold() == "unknown"]
        if unknown:
            findings.append(_finding(module_id, "low", "Device ownership unknown", f"{len(unknown)} device observation(s) lack a known owner.", "Assign ownership and location before operational follow-up.", (str(len(unknown)),)))
    elif module_id == "m12_orchestration":
        entries = _list(payload.get("entries")) or _list(payload.get("artifacts"))
        stored_count = int(payload.get("stored_evidence_count") or 0)
        unverified_count = int(payload.get("unverified_stored_evidence_count") or 0)
        if entries:
            findings.append(_finding(
                module_id,
                "info",
                "Evidence ledger built",
                f"{len(entries)} persisted artifact(s) were indexed.",
                "Use the ledger hash list to select evidence for review and reporting.",
                (str(len(entries)),),
            ))
        if stored_count:
            findings.append(_finding(
                module_id,
                "info",
                "EvidenceStore records indexed in ledger",
                f"{stored_count} EvidenceStore record(s) were included in the custody ledger.",
                "Review the ledger verification status before relying on stored evidence in reports or action plans.",
                (str(stored_count),),
            ))
        if unverified_count:
            unverified_refs = tuple(
                str(_dict(item).get("evidence_id") or _dict(item).get("id") or "")
                for item in entries
                if str(_dict(item).get("content_read_status") or "").casefold() == "unverified"
            )
            unverified_refs = tuple(ref for ref in unverified_refs if ref)[:10]
            findings.append(_finding(
                module_id,
                "high",
                "Stored evidence failed verification",
                f"{unverified_count} EvidenceStore record(s) could not be verified from the ledger content check.",
                "Quarantine the affected evidence, restore trusted content if available, and re-run verification before using it operationally.",
                unverified_refs or (str(unverified_count),),
            ))
    elif module_id == "m13_android":
        inspection = _dict(payload.get("inspection"))
        permissions = _list(inspection.get("permissions"))
        if permissions:
            findings.append(_finding(module_id, "medium", "APK declares permissions", f"The uploaded APK declares {len(permissions)} permission(s).", "Review manifest permissions against expected app behaviour.", (str(len(permissions)),)))
    elif module_id == "m14_phishing":
        summary = _dict(payload.get("outcome_summary"))
        counts = _dict(summary.get("event_count_by_type"))
        risky_events = sum(int(counts.get(key, 0) or 0) for key in ("clicked", "submitted", "reported_after_click"))
        if risky_events:
            findings.append(_finding(module_id, "medium", "Awareness campaign risky outcomes imported", f"{risky_events} click/submission-style outcome(s) were recorded.", "Prioritise targeted coaching and control validation for affected groups.", (str(risky_events),)))
    elif module_id == "m15_cloud":
        summary = _dict(payload.get("summary"))
        public_count = int(summary.get("public_asset_count") or 0)
        redacted_count = int(summary.get("redacted_attribute_count") or 0)
        if public_count:
            findings.append(_finding(module_id, "high", "Public cloud assets imported", f"{public_count} public cloud/container/Kubernetes asset(s) were observed.", "Validate exposure against approved architecture and harden access policies.", tuple(str(item) for item in _list(summary.get("public_asset_refs")))))
        if redacted_count:
            findings.append(_finding(module_id, "info", "Sensitive cloud attributes redacted", f"{redacted_count} sensitive attribute field(s) were removed during import.", "Review original export custody and rotate any exposed secrets if needed.", (str(redacted_count),)))
    return tuple(findings)
