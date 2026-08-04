"""Deterministic attack-surface graph built from stored target facts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from app.core.module_catalog import get_module_by_id
from app.core.target_fingerprint import TargetFingerprint
from app.core.target_model import TargetRecord

ATTACK_SURFACE_GRAPH_SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class AttackSurfaceNode:
    """A factual node in the target attack-surface graph."""

    node_id: str
    node_type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "properties": self.properties,
        }


@dataclass(frozen=True, slots=True)
class AttackSurfaceEdge:
    """A factual relationship between two graph nodes."""

    source_id: str
    target_id: str
    relationship: str
    confidence: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship": self.relationship,
            "confidence": self.confidence,
            "properties": self.properties,
        }


@dataclass(frozen=True, slots=True)
class AttackSurfaceGraph:
    """Serializable graph for one target without active discovery."""

    target_id: str
    schema_version: int
    nodes: tuple[AttackSurfaceNode, ...]
    edges: tuple[AttackSurfaceEdge, ...]
    source: str
    checksum: str

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "target_id": self.target_id,
            "source": self.source,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "checksum": self.checksum,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }


def _node_id(node_type: str, value: str) -> str:
    return f"{node_type}:{value.strip().lower()}"


def _add_node(nodes: dict[str, AttackSurfaceNode], node: AttackSurfaceNode) -> None:
    nodes.setdefault(node.node_id, node)


def _add_edge(edges: dict[tuple[str, str, str], AttackSurfaceEdge], edge: AttackSurfaceEdge) -> None:
    edges.setdefault((edge.source_id, edge.target_id, edge.relationship), edge)


def _checksum(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _surface_node_for_fingerprint(fingerprint: TargetFingerprint) -> AttackSurfaceNode:
    facts = fingerprint.fingerprint
    kind = str(facts.get("kind", fingerprint.target_type))
    if kind == "domain":
        value = str(facts["domain"])
        return AttackSurfaceNode(_node_id("domain", value), "domain", value, {"source": "target_fingerprint"})
    if kind == "ip":
        value = str(facts["ip"])
        return AttackSurfaceNode(_node_id("ip", value), "ip", value, {"source": "target_fingerprint"})
    if kind == "range":
        value = str(facts["cidr"])
        return AttackSurfaceNode(_node_id("network", value), "network", value, {"source": "target_fingerprint"})
    if kind == "url":
        value = str(facts["url"])
        return AttackSurfaceNode(_node_id("url", value), "url", value, {"source": "target_fingerprint"})
    if kind == "email":
        value = str(facts["email"])
        return AttackSurfaceNode(_node_id("email", value), "email", value, {"source": "target_fingerprint"})
    value = str(facts.get("value", fingerprint.normalized_value))
    return AttackSurfaceNode(_node_id(kind, value), kind, value, {"source": "target_fingerprint"})


def build_attack_surface_graph(target: TargetRecord, fingerprint: TargetFingerprint) -> AttackSurfaceGraph:
    """Build a deterministic passive graph from target metadata and fingerprint facts."""
    nodes: dict[str, AttackSurfaceNode] = {}
    edges: dict[tuple[str, str, str], AttackSurfaceEdge] = {}

    target_node_id = _node_id("target", target.target_id)
    target_node = AttackSurfaceNode(
        target_node_id,
        "target",
        target.name,
        {
            "target_type": target.target_type,
            "normalized_value": target.normalized_value,
            "mode": target.mode,
            "execution_implied": False,
        },
    )
    _add_node(nodes, target_node)

    surface_node = _surface_node_for_fingerprint(fingerprint)
    _add_node(nodes, surface_node)
    _add_edge(
        edges,
        AttackSurfaceEdge(
            target_node.node_id,
            surface_node.node_id,
            "HAS_ATTACK_SURFACE",
            confidence=fingerprint.confidence,
            properties={"fingerprint_tags": list(fingerprint.tags)},
        ),
    )

    facts = fingerprint.fingerprint
    kind = str(facts.get("kind", fingerprint.target_type))
    if kind == "url":
        host = str(facts.get("host", "")).strip().lower()
        if host:
            host_node = AttackSurfaceNode(_node_id("domain", host), "domain", host, {"source": "url_host"})
            _add_node(nodes, host_node)
            _add_edge(edges, AttackSurfaceEdge(surface_node.node_id, host_node.node_id, "URL_HOSTS_ON"))
        scheme = str(facts.get("scheme", "")).strip().lower()
        if scheme:
            scheme_node = AttackSurfaceNode(_node_id("protocol", scheme), "protocol", scheme, {"source": "url_scheme"})
            _add_node(nodes, scheme_node)
            _add_edge(edges, AttackSurfaceEdge(surface_node.node_id, scheme_node.node_id, "USES_PROTOCOL"))
    elif kind == "email":
        domain = str(facts.get("domain", "")).strip().lower()
        if domain:
            domain_node = AttackSurfaceNode(_node_id("domain", domain), "domain", domain, {"source": "email_domain"})
            _add_node(nodes, domain_node)
            _add_edge(edges, AttackSurfaceEdge(surface_node.node_id, domain_node.node_id, "EMAIL_USES_DOMAIN"))

    for module_id in target.allowed_modules:
        module = get_module_by_id(module_id)
        if module is None:
            continue
        module_node = AttackSurfaceNode(
            _node_id("module", module.module_id),
            "module",
            module.display_name,
            {
                "module_id": module.module_id,
                "module_number": module.module_number,
                "reserved": module.reserved,
                "readiness": module.readiness,
            },
        )
        _add_node(nodes, module_node)
        _add_edge(edges, AttackSurfaceEdge(target_node.node_id, module_node.node_id, "ALLOWS_MODULE"))

    sorted_nodes = tuple(sorted(nodes.values(), key=lambda node: node.node_id))
    sorted_edges = tuple(sorted(edges.values(), key=lambda edge: (edge.source_id, edge.relationship, edge.target_id)))
    checksum_payload = {
        "schema_version": ATTACK_SURFACE_GRAPH_SCHEMA_VERSION,
        "target_id": target.target_id,
        "nodes": [node.to_dict() for node in sorted_nodes],
        "edges": [edge.to_dict() for edge in sorted_edges],
    }
    return AttackSurfaceGraph(
        target_id=target.target_id,
        schema_version=ATTACK_SURFACE_GRAPH_SCHEMA_VERSION,
        nodes=sorted_nodes,
        edges=sorted_edges,
        source="target_fingerprint",
        checksum=_checksum(checksum_payload),
    )
