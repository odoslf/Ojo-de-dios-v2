"""Finding derivation for real M01 passive OSINT snapshots."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.core.osint_domain_snapshot import DNSRecordSet, DomainSnapshot

SEVERITY_INFO = "info"
SEVERITY_LOW = "low"
SEVERITY_MEDIUM = "medium"
SEVERITY_HIGH = "high"


@dataclass(frozen=True, slots=True)
class M01Finding:
    """One actionable finding derived from passive M01 evidence."""

    finding_id: str
    title: str
    severity: str
    confidence: str
    description: str
    evidence: dict[str, object]
    recommendation: str
    source: str = "m01_passive_osint"

    def to_dict(self) -> dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "title": self.title,
            "severity": self.severity,
            "confidence": self.confidence,
            "description": self.description,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "source": self.source,
            "real_execution": True,
            "demo": False,
        }


def _finding_id(domain: str, key: str) -> str:
    digest = hashlib.sha256(f"m01:{domain}:{key}".encode("utf-8")).hexdigest()[:12]
    return f"m01-{digest}"


def _record_values(snapshot: DomainSnapshot, record_type: str) -> tuple[str, ...]:
    return tuple(value for record in snapshot.records if record.record_type == record_type for value in record.values)


def _record_status(snapshot: DomainSnapshot, record_type: str) -> tuple[str, ...]:
    return tuple(record.status for record in snapshot.records if record.record_type == record_type)


def _finding(domain: str, key: str, title: str, severity: str, confidence: str, description: str, evidence: dict[str, object], recommendation: str) -> M01Finding:
    return M01Finding(
        finding_id=_finding_id(domain, key),
        title=title,
        severity=severity,
        confidence=confidence,
        description=description,
        evidence=evidence,
        recommendation=recommendation,
    )


def derive_m01_passive_findings(snapshot: DomainSnapshot) -> tuple[M01Finding, ...]:
    """Build actionable findings from a passive snapshot without inventing results."""
    findings: list[M01Finding] = []
    assessment = snapshot.assessment
    mx_values = _record_values(snapshot, "MX")
    txt_values = _record_values(snapshot, "TXT")
    ns_values = _record_values(snapshot, "NS")

    if snapshot.status != "RESOLVED":
        findings.append(
            _finding(
                snapshot.domain,
                "dns_not_resolved",
                "Dominio sin resolución DNS útil",
                SEVERITY_MEDIUM,
                "high",
                "La consulta pasiva no obtuvo direcciones ni registros DNS resueltos suficientes para operar sobre el dominio.",
                {"status": snapshot.status, "dns_statuses": {record.record_type: record.status for record in snapshot.records}},
                "Verificar que el dominio está bien escrito, activo y dentro del scope antes de continuar.",
            )
        )

    if assessment and assessment.has_mail_exchange and not assessment.has_spf:
        findings.append(
            _finding(
                snapshot.domain,
                "mx_without_spf",
                "Correo publicado sin SPF detectado",
                SEVERITY_MEDIUM,
                "medium",
                "El dominio publica MX, pero en esta consulta TXT no se detectó un registro SPF.",
                {"mx_records": list(mx_values), "txt_records": list(txt_values)},
                "Revisar DNS y publicar un SPF válido si el dominio envía correo.",
            )
        )

    if assessment and assessment.has_mail_exchange and not assessment.has_dmarc:
        findings.append(
            _finding(
                snapshot.domain,
                "mx_without_dmarc",
                "Correo publicado sin DMARC detectado",
                SEVERITY_MEDIUM,
                "medium",
                "El dominio publica MX, pero en esta consulta no se detectó política DMARC.",
                {"mx_records": list(mx_values), "txt_statuses": list(_record_status(snapshot, "TXT"))},
                "Publicar una política DMARC alineada con SPF/DKIM y revisar reportes antes de endurecerla.",
            )
        )

    if assessment and not assessment.has_nameservers:
        findings.append(
            _finding(
                snapshot.domain,
                "no_ns_detected",
                "Nameservers no detectados en la consulta",
                SEVERITY_LOW,
                "medium",
                "La resolución pasiva no devolvió registros NS para el dominio consultado.",
                {"ns_records": list(ns_values), "ns_statuses": list(_record_status(snapshot, "NS"))},
                "Validar delegación DNS y servidores autoritativos antes de planificar técnicas posteriores.",
            )
        )

    certificate_name_count = assessment.certificate_name_count if assessment else 0
    if certificate_name_count >= 25:
        findings.append(
            _finding(
                snapshot.domain,
                "large_certificate_surface",
                "Superficie observable amplia en Certificate Transparency",
                SEVERITY_LOW,
                "medium",
                "Certificate Transparency muestra un número elevado de nombres asociados al dominio.",
                {"certificate_name_count": certificate_name_count},
                "Revisar los nombres observados, separar activos reales de históricos y priorizar inventario autorizado.",
            )
        )

    if not findings:
        findings.append(
            _finding(
                snapshot.domain,
                "baseline_recorded",
                "Baseline pasivo registrado sin hallazgos priorizados",
                SEVERITY_INFO,
                "high",
                "La ejecución dejó evidencia pasiva usable, pero no generó hallazgos accionables con las reglas actuales.",
                {"status": snapshot.status, "record_count": len(snapshot.records)},
                "Usar este baseline como punto de partida y activar fuentes externas pasivas si se requiere más contexto.",
            )
        )

    return tuple(findings)
