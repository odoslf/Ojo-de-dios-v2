"""Passive external OSINT sources for M01.

These helpers query public OSINT aggregation endpoints (RDAP and Certificate
Transparency) and never contact the target website or scan target services.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

RDAP_ORG_DOMAIN_URL = "https://rdap.org/domain/{domain}"
CRTSH_JSON_URL = "https://crt.sh/"
DEFAULT_TIMEOUT_SECONDS = 20
DEFAULT_CT_LIMIT = 50


@dataclass(frozen=True, slots=True)
class PassiveSourceResult:
    """One external passive source result."""

    source: str
    status: str
    url: str
    summary: dict[str, object]
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "status": self.status,
            "url": self.url,
            "summary": self.summary,
            "error": self.error,
            "target_web_request_performed": False,
            "port_scan_performed": False,
        }


def _event_dates(payload: dict[str, Any]) -> dict[str, str]:
    dates: dict[str, str] = {}
    for event in payload.get("events", []):
        if not isinstance(event, dict):
            continue
        action = str(event.get("eventAction", "")).strip()
        date = str(event.get("eventDate", "")).strip()
        if action and date:
            dates[action] = date
    return dates


def _entity_names(payload: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for entity in payload.get("entities", []):
        if not isinstance(entity, dict):
            continue
        roles = ",".join(str(role) for role in entity.get("roles", []) if role)
        vcard = entity.get("vcardArray", [])
        display = ""
        if isinstance(vcard, list) and len(vcard) > 1 and isinstance(vcard[1], list):
            for item in vcard[1]:
                if isinstance(item, list) and len(item) >= 4 and item[0] in {"fn", "org"}:
                    display = str(item[3])
                    break
        if display:
            names.append(f"{roles}: {display}" if roles else display)
    return sorted(set(names))[:10]


def fetch_rdap_domain(domain: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> PassiveSourceResult:
    """Fetch public RDAP data through rdap.org for a domain."""
    url = RDAP_ORG_DOMAIN_URL.format(domain=domain)
    try:
        response = requests.get(url, timeout=timeout_seconds, headers={"Accept": "application/rdap+json, application/json"})
    except requests.RequestException as exc:
        return PassiveSourceResult("rdap", "ERROR", url, summary={}, error=str(exc))
    if response.status_code != 200:
        return PassiveSourceResult("rdap", "HTTP_ERROR", url, summary={"status_code": response.status_code}, error=response.text[:300])
    try:
        payload = response.json()
    except ValueError as exc:
        return PassiveSourceResult("rdap", "INVALID_JSON", url, summary={}, error=str(exc))
    statuses = payload.get("status", [])
    if not isinstance(statuses, list):
        statuses = [str(statuses)]
    summary = {
        "ldh_name": payload.get("ldhName"),
        "handle": payload.get("handle"),
        "statuses": [str(status) for status in statuses],
        "events": _event_dates(payload),
        "entities": _entity_names(payload),
    }
    return PassiveSourceResult("rdap", "READY", url, summary=summary)


def _normalize_ct_name(value: str, domain: str) -> tuple[str, ...]:
    names: list[str] = []
    for raw_name in value.split("\n"):
        name = raw_name.strip().lower().lstrip("*.").rstrip(".")
        if name and (name == domain or name.endswith(f".{domain}")):
            names.append(name)
    return tuple(names)


def fetch_certificate_transparency(domain: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS, limit: int = DEFAULT_CT_LIMIT) -> PassiveSourceResult:
    """Fetch passive certificate names from crt.sh JSON output."""
    url = f"{CRTSH_JSON_URL}?q=%25.{domain}&output=json"
    try:
        response = requests.get(CRTSH_JSON_URL, params={"q": f"%.{domain}", "output": "json"}, timeout=timeout_seconds)
    except requests.RequestException as exc:
        return PassiveSourceResult("certificate_transparency", "ERROR", url, summary={}, error=str(exc))
    if response.status_code != 200:
        return PassiveSourceResult("certificate_transparency", "HTTP_ERROR", url, summary={"status_code": response.status_code}, error=response.text[:300])
    try:
        payload = response.json()
    except ValueError as exc:
        return PassiveSourceResult("certificate_transparency", "INVALID_JSON", url, summary={}, error=str(exc))
    if not isinstance(payload, list):
        return PassiveSourceResult("certificate_transparency", "INVALID_JSON", url, summary={}, error="crt.sh did not return a list")
    names: set[str] = set()
    issuers: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            continue
        names.update(_normalize_ct_name(str(item.get("name_value", "")), domain))
        issuer = str(item.get("issuer_name", "")).strip()
        if issuer:
            issuers.add(issuer)
    sorted_names = sorted(names)
    summary = {
        "name_count": len(sorted_names),
        "names": sorted_names[:limit],
        "truncated": len(sorted_names) > limit,
        "issuers": sorted(issuers)[:10],
    }
    return PassiveSourceResult("certificate_transparency", "READY", url, summary=summary)


def fetch_external_passive_sources(domain: str) -> tuple[PassiveSourceResult, ...]:
    """Fetch all currently supported external passive sources for M01."""
    return (
        fetch_rdap_domain(domain),
        fetch_certificate_transparency(domain),
    )
