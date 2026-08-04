"""Passive OSINT domain snapshot helpers for M01.

This module performs only passive DNS/RDAP-style preparation with local resolver
queries. It does not scan ports, crawl sites, brute-force names, or contact the
HTTP service of the target domain.
"""

from __future__ import annotations

import ipaddress
import json
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import dns.exception
import dns.resolver

from app.core.osint_passive_sources import PassiveSourceResult, fetch_external_passive_sources

DNS_RECORD_TYPES = ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA")


@dataclass(frozen=True, slots=True)
class DNSRecordSet:
    """One DNS record-set observed for a domain."""

    record_type: str
    values: tuple[str, ...]
    status: str
    error: str | None = None
    def to_dict(self) -> dict[str, object]:
        return {
            "record_type": self.record_type,
            "values": list(self.values),
            "status": self.status,
            "error": self.error,
        }


@dataclass(frozen=True, slots=True)
class DomainAssessment:
    """Operational interpretation of passive DNS records."""

    has_ipv4: bool
    has_ipv6: bool
    has_nameservers: bool
    has_mail_exchange: bool
    has_spf: bool
    has_dmarc: bool
    exposure_notes: tuple[str, ...]
    external_source_count: int = 0
    rdap_available: bool = False
    certificate_name_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "has_ipv4": self.has_ipv4,
            "has_ipv6": self.has_ipv6,
            "has_nameservers": self.has_nameservers,
            "has_mail_exchange": self.has_mail_exchange,
            "has_spf": self.has_spf,
            "has_dmarc": self.has_dmarc,
            "exposure_notes": list(self.exposure_notes),
            "external_source_count": self.external_source_count,
            "rdap_available": self.rdap_available,
            "certificate_name_count": self.certificate_name_count,
        }


@dataclass(frozen=True, slots=True)
class DomainSnapshot:
    """Auditable passive OSINT snapshot for one domain."""

    domain: str
    addresses: tuple[str, ...]
    canonical_name: str | None
    status: str
    checked_at: str
    records: tuple[DNSRecordSet, ...] = ()
    error: str | None = None
    assessment: DomainAssessment | None = None
    external_sources: tuple[PassiveSourceResult, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "domain": self.domain,
            "addresses": list(self.addresses),
            "canonical_name": self.canonical_name,
            "status": self.status,
            "checked_at": self.checked_at,
            "records": [record.to_dict() for record in self.records],
            "assessment": self.assessment.to_dict() if self.assessment else None,
            "external_sources": [source.to_dict() for source in self.external_sources],
            "error": self.error,
            "passive_dns_only": True,
            "port_scan_performed": False,
            "web_request_performed": False,
            "subdomain_bruteforce_performed": False,
        }


def normalize_domain(value: str) -> str:
    """Normalize a user supplied domain/hostname without accepting URLs or IPs."""
    domain = value.strip().lower().rstrip(".")
    if not domain or "://" in domain or "/" in domain or "@" in domain:
        raise ValueError("Introduce solo un dominio, sin http://, rutas ni correos.")
    if len(domain) > 253 or any(part == "" for part in domain.split(".")):
        raise ValueError("Dominio no válido.")
    try:
        ipaddress.ip_address(domain)
    except ValueError:
        pass
    else:
        raise ValueError("Este flujo M01 espera dominio, no IP directa.")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-.")
    if any(char not in allowed for char in domain):
        raise ValueError("Dominio contiene caracteres no permitidos.")
    if any(part.startswith("-") or part.endswith("-") for part in domain.split(".")):
        raise ValueError("Dominio no válido.")
    return domain


def _resolve_socket_addresses(domain: str) -> tuple[str | None, tuple[str, ...], str | None]:
    try:
        canonical_name, _, raw_addresses = socket.gethostbyname_ex(domain)
    except socket.gaierror as exc:
        return None, (), str(exc)
    return canonical_name or None, tuple(sorted(set(raw_addresses))), None


def _record_text(record: object) -> str:
    text = record.to_text() if hasattr(record, "to_text") else str(record)
    return text.strip().strip('"')


def _resolve_record_set(domain: str, record_type: str, resolver: dns.resolver.Resolver) -> DNSRecordSet:
    try:
        answer = resolver.resolve(domain, record_type, raise_on_no_answer=False)
    except dns.resolver.NXDOMAIN as exc:
        return DNSRecordSet(record_type=record_type, values=(), status="NXDOMAIN", error=str(exc))
    except dns.resolver.NoNameservers as exc:
        return DNSRecordSet(record_type=record_type, values=(), status="NO_NAMESERVERS", error=str(exc))
    except dns.resolver.LifetimeTimeout as exc:
        return DNSRecordSet(record_type=record_type, values=(), status="TIMEOUT", error=str(exc))
    except dns.exception.DNSException as exc:
        return DNSRecordSet(record_type=record_type, values=(), status="ERROR", error=str(exc))
    values = tuple(sorted({_record_text(item) for item in answer}))
    if not values:
        return DNSRecordSet(record_type=record_type, values=(), status="NO_ANSWER")
    return DNSRecordSet(record_type=record_type, values=values, status="RESOLVED")


def _values_for(records: tuple[DNSRecordSet, ...], record_type: str) -> tuple[str, ...]:
    return tuple(value for record in records if record.record_type == record_type for value in record.values)


def build_domain_assessment(
    records: tuple[DNSRecordSet, ...], external_sources: tuple[PassiveSourceResult, ...] = ()
) -> DomainAssessment:
    """Derive an operational passive-OSINT assessment from DNS records."""
    a_values = _values_for(records, "A")
    aaaa_values = _values_for(records, "AAAA")
    ns_values = _values_for(records, "NS")
    mx_values = _values_for(records, "MX")
    txt_values = _values_for(records, "TXT")
    txt_lower = tuple(value.lower() for value in txt_values)
    has_spf = any(value.startswith("v=spf1") for value in txt_lower)
    has_dmarc = any("v=dmarc1" in value for value in txt_lower)
    notes: list[str] = []
    if a_values:
        notes.append("IPv4 publicado")
    if aaaa_values:
        notes.append("IPv6 publicado")
    if ns_values:
        notes.append("Nameservers publicados")
    if mx_values:
        notes.append("Correo publicado por MX")
    if has_spf:
        notes.append("SPF detectado en TXT")
    if has_dmarc:
        notes.append("DMARC detectado en TXT")
    if mx_values and not has_spf:
        notes.append("MX sin SPF detectado en esta consulta")
    if mx_values and not has_dmarc:
        notes.append("MX sin DMARC detectado en esta consulta")
    rdap_available = any(source.source == "rdap" and source.status == "READY" for source in external_sources)
    certificate_name_count = 0
    for source in external_sources:
        if source.source == "certificate_transparency" and source.status == "READY":
            raw_count = source.summary.get("name_count", 0)
            if isinstance(raw_count, int):
                certificate_name_count = raw_count
    if rdap_available:
        notes.append("RDAP público disponible")
    if certificate_name_count:
        notes.append(f"Certificate Transparency con {certificate_name_count} nombre(s) observado(s)")
    if not notes:
        notes.append("Sin registros DNS útiles en esta consulta")
    return DomainAssessment(
        has_ipv4=bool(a_values),
        has_ipv6=bool(aaaa_values),
        has_nameservers=bool(ns_values),
        has_mail_exchange=bool(mx_values),
        has_spf=has_spf,
        has_dmarc=has_dmarc,
        exposure_notes=tuple(notes),
        external_source_count=len(external_sources),
        rdap_available=rdap_available,
        certificate_name_count=certificate_name_count,
    )


def build_passive_domain_snapshot(
    domain: str,
    record_types: tuple[str, ...] = DNS_RECORD_TYPES,
    include_external: bool = False,
) -> DomainSnapshot:
    """Resolve a domain with passive DNS queries and return an honest status."""
    normalized = normalize_domain(domain)
    checked_at = datetime.now(timezone.utc).isoformat()
    canonical_name, socket_addresses, socket_error = _resolve_socket_addresses(normalized)
    resolver = dns.resolver.Resolver(configure=True)
    resolver.lifetime = 5.0
    resolver.timeout = 3.0
    records = tuple(_resolve_record_set(normalized, record_type, resolver) for record_type in record_types)
    record_addresses = tuple(
        sorted(
            {
                value
                for record in records
                if record.record_type in {"A", "AAAA"} and record.status == "RESOLVED"
                for value in record.values
            }
        )
    )
    addresses = tuple(sorted(set(socket_addresses + record_addresses)))
    external_sources = fetch_external_passive_sources(normalized) if include_external else ()
    resolved_record_count = len([record for record in records if record.status == "RESOLVED"])
    status = "RESOLVED" if addresses or resolved_record_count else "DNS_NOT_RESOLVED"
    return DomainSnapshot(
        domain=normalized,
        addresses=addresses,
        canonical_name=canonical_name,
        status=status,
        checked_at=checked_at,
        records=records,
        error=None if status == "RESOLVED" else socket_error,
        assessment=build_domain_assessment(records, external_sources),
        external_sources=external_sources,
    )


def write_domain_snapshot(snapshot: DomainSnapshot, repo_root: Path | None = None) -> Path:
    """Persist the snapshot in the M01 workspace as real JSON evidence."""
    root = Path.cwd() if repo_root is None else repo_root
    safe_name = snapshot.domain.replace(".", "_")
    target_dir = root / "storage" / "workspaces" / "m01_osint" / "passive_dns"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{safe_name}.json"
    target_path.write_text(json.dumps(snapshot.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target_path
