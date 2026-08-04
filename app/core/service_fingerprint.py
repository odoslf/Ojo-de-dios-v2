"""Passive service fingerprinting from target facts and operator metadata."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.core.target_fingerprint import TargetFingerprint
from app.core.target_model import TargetRecord

SERVICE_FINGERPRINT_SCHEMA_VERSION = 1
_DEFAULT_PORT_BY_SCHEME = {"http": 80, "https": 443}


@dataclass(frozen=True, slots=True)
class ServiceEndpointFingerprint:
    """One passive service endpoint fingerprint."""

    endpoint_id: str
    host: str
    port: int
    transport: str
    service_name: str
    source: str
    confidence: float
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "endpoint_id": self.endpoint_id,
            "host": self.host,
            "port": self.port,
            "transport": self.transport,
            "service_name": self.service_name,
            "source": self.source,
            "confidence": self.confidence,
            "properties": self.properties,
        }


@dataclass(frozen=True, slots=True)
class ServiceFingerprintReport:
    """Passive service fingerprint report for a target."""

    target_id: str
    schema_version: int
    endpoints: tuple[ServiceEndpointFingerprint, ...]
    checksum: str
    execution_started: bool = False

    @property
    def endpoint_count(self) -> int:
        return len(self.endpoints)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "target_id": self.target_id,
            "endpoint_count": self.endpoint_count,
            "checksum": self.checksum,
            "execution_started": self.execution_started,
            "endpoints": [endpoint.to_dict() for endpoint in self.endpoints],
        }


def _validate_port(port: Any) -> int:
    if isinstance(port, bool):
        raise ValueError("Service port must be an integer.")
    try:
        parsed = int(port)
    except (TypeError, ValueError) as exc:
        raise ValueError("Service port must be an integer.") from exc
    if parsed < 1 or parsed > 65535:
        raise ValueError("Service port must be between 1 and 65535.")
    return parsed


def _normalize_transport(value: Any) -> str:
    transport = str(value or "tcp").strip().lower()
    if transport not in {"tcp", "udp"}:
        raise ValueError("Service transport must be tcp or udp.")
    return transport


def _endpoint_id(host: str, port: int, transport: str, service_name: str) -> str:
    return f"{transport}:{host.lower()}:{port}:{service_name.lower()}"


def _checksum(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _endpoint_from_url_fingerprint(fingerprint: TargetFingerprint) -> ServiceEndpointFingerprint | None:
    facts = fingerprint.fingerprint
    if facts.get("kind") != "url":
        return None
    scheme = str(facts.get("scheme", "")).strip().lower()
    host = str(facts.get("host", "")).strip().lower()
    if scheme not in _DEFAULT_PORT_BY_SCHEME or not host:
        return None
    port = _validate_port(facts.get("port") or _DEFAULT_PORT_BY_SCHEME[scheme])
    service_name = scheme
    properties = {
        "url": facts.get("url", fingerprint.normalized_value),
        "path": facts.get("path", ""),
        "inferred_from": "url_scheme",
    }
    return ServiceEndpointFingerprint(
        endpoint_id=_endpoint_id(host, port, "tcp", service_name),
        host=host,
        port=port,
        transport="tcp",
        service_name=service_name,
        source="target_fingerprint",
        confidence=min(float(fingerprint.confidence), 0.95),
        properties=properties,
    )


def _endpoints_from_metadata(target: TargetRecord) -> list[ServiceEndpointFingerprint]:
    raw_services = target.metadata.get("services", [])
    if raw_services is None:
        return []
    if not isinstance(raw_services, list):
        raise ValueError("target.metadata.services must be a list.")
    endpoints: list[ServiceEndpointFingerprint] = []
    for index, raw_service in enumerate(raw_services):
        if not isinstance(raw_service, dict):
            raise ValueError("Each target.metadata.services entry must be an object.")
        host = str(raw_service.get("host") or target.normalized_value).strip().lower()
        if not host:
            raise ValueError("Service host cannot be empty.")
        port = _validate_port(raw_service.get("port"))
        transport = _normalize_transport(raw_service.get("transport", "tcp"))
        service_name = str(raw_service.get("service_name") or raw_service.get("name") or "unknown").strip().lower()
        if not service_name:
            raise ValueError("Service name cannot be empty.")
        confidence_raw = raw_service.get("confidence", 0.75)
        try:
            confidence = float(confidence_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("Service confidence must be numeric.") from exc
        confidence = max(0.0, min(confidence, 1.0))
        properties = {
            "metadata_index": index,
            "operator_supplied": True,
        }
        if "product" in raw_service:
            properties["product"] = str(raw_service["product"])
        if "version" in raw_service:
            properties["version"] = str(raw_service["version"])
        endpoints.append(
            ServiceEndpointFingerprint(
                endpoint_id=_endpoint_id(host, port, transport, service_name),
                host=host,
                port=port,
                transport=transport,
                service_name=service_name,
                source="target_metadata",
                confidence=confidence,
                properties=properties,
            )
        )
    return endpoints


def build_service_fingerprint_report(target: TargetRecord, fingerprint: TargetFingerprint) -> ServiceFingerprintReport:
    """Build passive service fingerprints from local facts; never scans the target."""
    endpoints_by_id: dict[str, ServiceEndpointFingerprint] = {}
    url_endpoint = _endpoint_from_url_fingerprint(fingerprint)
    if url_endpoint is not None:
        endpoints_by_id[url_endpoint.endpoint_id] = url_endpoint
    for endpoint in _endpoints_from_metadata(target):
        endpoints_by_id[endpoint.endpoint_id] = endpoint
    endpoints = tuple(sorted(endpoints_by_id.values(), key=lambda endpoint: endpoint.endpoint_id))
    checksum_payload = {
        "schema_version": SERVICE_FINGERPRINT_SCHEMA_VERSION,
        "target_id": target.target_id,
        "endpoints": [endpoint.to_dict() for endpoint in endpoints],
    }
    return ServiceFingerprintReport(
        target_id=target.target_id,
        schema_version=SERVICE_FINGERPRINT_SCHEMA_VERSION,
        endpoints=endpoints,
        checksum=_checksum(checksum_payload),
    )
