"""Defensive M18 honeypot/deception techniques.

The R19 base implementation is defensive-only: it prepares isolated honeypot
configuration bundles, parses operator-supplied honeypot logs, extracts IOCs and
profiles observed intrusions passively.  It does not exploit systems, run
countermeasures, beacon to infrastructure, or launch network services itself.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.contracts.evidence_contract import EVIDENCE_QUALITY_HIGH, EVIDENCE_QUALITY_MEDIUM, EvidenceRecord, RESULT_SUCCESS
from app.contracts.technique_contract import BaseTechnique, STATUS_READY_CONTROLLED, TechniqueExecutionContext, TechniqueExecutionResult
from app.core.errors import ContractError
from app.core.technique_evidence_utils import stable_evidence_id, utc_now_iso
from app.core.permission_levels import PERMISSION_PASSIVE

M18_MODULE_ID = "m18_honeypots_deception"
_ALLOWED_PROFILES = {"ssh", "http", "canary_tcp"}
_MAX_LOG_BYTES = 5_000_000
_PRIVATE_NETS = tuple(ipaddress.ip_network(net) for net in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "127.0.0.0/8", "169.254.0.0/16", "::1/128", "fc00::/7", "fe80::/10"))
_IP_PATTERN = re.compile(r"(?<![\w:.])(?:\d{1,3}\.){3}\d{1,3}(?![\w:.])")
_HASH_PATTERN = re.compile(r"\b(?:[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64})\b")
_URL_PATTERN = re.compile(r"https?://[^\s'\"]+")
_USER_PATTERN = re.compile(r"(?:user(?:name)?|login)[:= ]+['\"]?([A-Za-z0-9._@+-]{1,64})", re.IGNORECASE)
_PATH_PATTERN = re.compile(r"\b(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+([^\s]+)", re.IGNORECASE)
_AGENT_PATTERN = re.compile(r"user-agent[:= ]+['\"]?([^'\"\n]{3,200})", re.IGNORECASE)

def _evidence(context: TechniqueExecutionContext, technique_id: str, suffix: str, summary: str, content: dict[str, Any], *, quality: str = EVIDENCE_QUALITY_HIGH) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=stable_evidence_id(context.run_id, technique_id, suffix),
        run_id=context.run_id,
        target_id=context.target_id,
        technique_id=technique_id,
        module_id=M18_MODULE_ID,
        evidence_type=suffix,
        quality=quality,
        summary=summary,
        content=content,
        source="m18-defensive-deception",
        demo=False,
        real_execution=True,
        created_at=utc_now_iso(),
    )


def _safe_name(value: Any, field_name: str) -> str:
    text = str(value or "").strip().lower().replace("_", "-")
    if not re.fullmatch(r"[a-z0-9.-]{1,64}", text):
        raise ContractError(f"{field_name} must contain only letters, numbers, dot or dash.")
    return text


def _profile_list(value: Any) -> list[str]:
    if value is None:
        return ["ssh", "http", "canary_tcp"]
    if not isinstance(value, list) or not value:
        raise ContractError("profiles must be a non-empty list when provided.")
    profiles = [_safe_name(item, "profile").replace("-", "_") for item in value]
    invalid = sorted(set(profiles) - _ALLOWED_PROFILES)
    if invalid:
        raise ContractError(f"unsupported honeypot profiles: {', '.join(invalid)}")
    return sorted(set(profiles))


def _read_json_or_lines(parameters: dict[str, Any], content_name: str, path_name: str) -> Any:
    if parameters.get(content_name) is not None:
        return parameters[content_name]
    path_text = str(parameters.get(path_name, "")).strip()
    if not path_text:
        raise ContractError(f"{content_name} or {path_name} is required.")
    path = Path(path_text)
    if not path.is_file():
        raise ContractError(f"{path_name} does not point to a readable file.")
    if path.stat().st_size > _MAX_LOG_BYTES:
        raise ContractError(f"{path_name} exceeds maximum supported size.")
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text.splitlines()


def _valid_ip(value: str) -> str | None:
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return None


def _ip_scope(ip_text: str) -> str:
    ip = ipaddress.ip_address(ip_text)
    return "private" if any(ip in network for network in _PRIVATE_NETS) else "public"


def _line_events(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("events"), list):
        raw_events = payload["events"]
    elif isinstance(payload, list):
        raw_events = payload
    else:
        raise ContractError("honeypot log input must be a list or an object with events list.")
    events: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_events):
        if isinstance(raw, dict):
            message = str(raw.get("message") or raw.get("event") or raw.get("raw") or "")
            source_ip = str(raw.get("src_ip") or raw.get("source_ip") or raw.get("remote_addr") or "")
            event_type = str(raw.get("event_type") or raw.get("type") or "interaction")
            timestamp = raw.get("timestamp") or raw.get("time")
        else:
            message = str(raw)
            source_ip = ""
            event_type = "interaction"
            timestamp = None
        if not source_ip:
            match = _IP_PATTERN.search(message)
            source_ip = match.group(0) if match else ""
        valid_ip = _valid_ip(source_ip) if source_ip else None
        events.append({
            "event_index": index,
            "timestamp": str(timestamp) if timestamp else None,
            "src_ip": valid_ip,
            "ip_scope": _ip_scope(valid_ip) if valid_ip else "unknown",
            "event_type": event_type,
            "message": message[:1_000],
        })
    if not events:
        raise ContractError("honeypot log input must include at least one event.")
    return events


def _extract_iocs(events: list[dict[str, Any]]) -> dict[str, list[str]]:
    ips = sorted({event["src_ip"] for event in events if event.get("src_ip")})
    urls: set[str] = set()
    hashes: set[str] = set()
    usernames: set[str] = set()
    paths: set[str] = set()
    user_agents: set[str] = set()
    for event in events:
        message = str(event.get("message") or "")
        urls.update(match.rstrip('.,);]') for match in _URL_PATTERN.findall(message))
        hashes.update(match.lower() for match in _HASH_PATTERN.findall(message))
        usernames.update(match.group(1) for match in _USER_PATTERN.finditer(message))
        paths.update(match.group(1)[:300] for match in _PATH_PATTERN.finditer(message))
        user_agents.update(match.group(1).strip() for match in _AGENT_PATTERN.finditer(message))
    return {
        "ip_addresses": ips,
        "urls": sorted(urls),
        "hashes": sorted(hashes),
        "usernames": sorted(usernames),
        "http_paths": sorted(paths),
        "user_agents": sorted(user_agents),
    }


def _profile_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    by_ip: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if event.get("src_ip"):
            by_ip[str(event["src_ip"])].append(event)
    profiles: list[dict[str, Any]] = []
    for src_ip, ip_events in sorted(by_ip.items()):
        messages = "\n".join(str(event.get("message") or "") for event in ip_events).lower()
        tags: set[str] = set()
        if len(ip_events) >= 5 or any(word in messages for word in ("failed password", "invalid user", "login failed")):
            tags.add("credential_bruteforce")
        if any(path in messages for path in ("/.env", "/wp-login.php", "/admin", "phpmyadmin")):
            tags.add("web_probe")
        if any(word in messages for word in ("wget ", "curl ", "powershell", "chmod +x")):
            tags.add("payload_staging")
        if any(word in messages for word in ("masscan", "nmap", "zgrab", "gobuster", "sqlmap")):
            tags.add("scanner_tooling")
        profiles.append({
            "src_ip": src_ip,
            "ip_scope": _ip_scope(src_ip),
            "event_count": len(ip_events),
            "first_event_index": min(int(event["event_index"]) for event in ip_events),
            "last_event_index": max(int(event["event_index"]) for event in ip_events),
            "tags": sorted(tags) or ["unclassified_interaction"],
        })
    event_type_counts = Counter(str(event.get("event_type") or "unknown") for event in events)
    return {"actor_profiles": profiles, "event_type_counts": dict(sorted(event_type_counts.items())), "event_count": len(events)}



def _utc_from_event(event: dict[str, Any]) -> str:
    timestamp = event.get("timestamp")
    return str(timestamp) if timestamp else utc_now_iso()


def _ioc_rows_from_summary(iocs: dict[str, list[str]], events: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    first_seen = min((_utc_from_event(event) for event in events), default=utc_now_iso())
    last_seen = max((_utc_from_event(event) for event in events), default=first_seen)
    type_map = {
        "ip_addresses": "ip",
        "urls": "url",
        "hashes": "hash",
        "usernames": "username",
        "http_paths": "http_path",
        "user_agents": "user_agent",
    }
    for summary_key, ioc_type in type_map.items():
        for value in iocs.get(summary_key, []):
            rows.append({
                "ioc_type": ioc_type,
                "value": value,
                "source": source,
                "first_seen": first_seen,
                "last_seen": last_seen,
                "ip_scope": _ip_scope(value) if ioc_type == "ip" else None,
            })
    return rows


def _init_ioc_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ioc_history (
                ioc_id TEXT PRIMARY KEY,
                ioc_type TEXT NOT NULL,
                value TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                observation_count INTEGER NOT NULL,
                sources_json TEXT NOT NULL,
                ip_scope TEXT,
                confidence_score REAL NOT NULL,
                confidence_level TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ioc_history_type_value ON ioc_history(ioc_type, value)")
        connection.commit()


def _confidence_for_ioc(ioc_type: str, value: str, observation_count: int, source_count: int, ip_scope: str | None) -> tuple[float, str, list[str]]:
    reasons: list[str] = []
    score = 0.25
    if observation_count >= 2:
        score += min(0.25, 0.08 * (observation_count - 1))
        reasons.append("repeated_observations")
    if source_count >= 2:
        score += 0.20
        reasons.append("multiple_sources")
    if ioc_type in {"hash", "url"}:
        score += 0.15
        reasons.append("high_specificity_indicator")
    if ioc_type == "ip" and ip_scope == "public":
        score += 0.10
        reasons.append("public_routable_ip")
    if ioc_type in {"username", "http_path", "user_agent"}:
        score += 0.05
        reasons.append("behavioral_indicator")
    score = max(0.0, min(1.0, round(score, 3)))
    if score >= 0.75:
        level = "high"
    elif score >= 0.5:
        level = "medium"
    else:
        level = "low"
    return score, level, reasons


def persist_ioc_history(db_path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Persist IOC observations to SQLite and return scored current inventory."""
    _init_ioc_db(db_path)
    now = utc_now_iso()
    changed = 0
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        for row in rows:
            ioc_type = str(row["ioc_type"])
            value = str(row["value"])
            ioc_id = hashlib.sha256(f"{ioc_type}:{value}".encode("utf-8")).hexdigest()
            existing = connection.execute("SELECT * FROM ioc_history WHERE ioc_id = ?", (ioc_id,)).fetchone()
            source = str(row.get("source") or "operator_supplied")
            ip_scope = row.get("ip_scope")
            if existing is None:
                sources = [source]
                observation_count = 1
                first_seen = str(row["first_seen"])
                last_seen = str(row["last_seen"])
            else:
                sources = sorted(set(json.loads(str(existing["sources_json"])) + [source]))
                observation_count = int(existing["observation_count"]) + 1
                first_seen = min(str(existing["first_seen"]), str(row["first_seen"]))
                last_seen = max(str(existing["last_seen"]), str(row["last_seen"]))
                ip_scope = ip_scope or existing["ip_scope"]
            confidence, level, _ = _confidence_for_ioc(ioc_type, value, observation_count, len(sources), str(ip_scope) if ip_scope else None)
            connection.execute(
                """
                INSERT INTO ioc_history(ioc_id, ioc_type, value, first_seen, last_seen, observation_count, sources_json, ip_scope, confidence_score, confidence_level, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ioc_id) DO UPDATE SET
                    first_seen=excluded.first_seen,
                    last_seen=excluded.last_seen,
                    observation_count=excluded.observation_count,
                    sources_json=excluded.sources_json,
                    ip_scope=excluded.ip_scope,
                    confidence_score=excluded.confidence_score,
                    confidence_level=excluded.confidence_level,
                    updated_at=excluded.updated_at
                """,
                (ioc_id, ioc_type, value, first_seen, last_seen, observation_count, json.dumps(sources, ensure_ascii=False), ip_scope, confidence, level, now),
            )
            changed += 1
        connection.commit()
        stored = connection.execute("SELECT * FROM ioc_history ORDER BY confidence_score DESC, ioc_type, value").fetchall()
    inventory: list[dict[str, Any]] = []
    for item in stored:
        confidence, level, reasons = _confidence_for_ioc(item["ioc_type"], item["value"], int(item["observation_count"]), len(json.loads(item["sources_json"])), item["ip_scope"])
        inventory.append({
            "ioc_id": item["ioc_id"],
            "ioc_type": item["ioc_type"],
            "value": item["value"],
            "first_seen": item["first_seen"],
            "last_seen": item["last_seen"],
            "observation_count": int(item["observation_count"]),
            "sources": json.loads(item["sources_json"]),
            "source_count": len(json.loads(item["sources_json"])),
            "ip_scope": item["ip_scope"],
            "confidence_score": confidence,
            "confidence_level": level,
            "confidence_reasons": reasons,
        })
    return {"db_path": db_path.as_posix(), "changed_observations": changed, "ioc_count": len(inventory), "iocs": inventory}


def _actor_confidence_profiles(events: list[dict[str, Any]]) -> dict[str, Any]:
    profile = _profile_events(events)
    enriched: list[dict[str, Any]] = []
    for actor in profile["actor_profiles"]:
        tag_count = len(actor.get("tags", []))
        event_count = int(actor.get("event_count", 0))
        score = min(1.0, round(0.20 + min(0.35, event_count * 0.07) + min(0.30, tag_count * 0.10) + (0.10 if actor.get("ip_scope") == "public" else 0.0), 3))
        actor = dict(actor)
        actor["confidence_score"] = score
        actor["confidence_level"] = "high" if score >= 0.75 else "medium" if score >= 0.5 else "low"
        enriched.append(actor)
    profile["actor_profiles"] = enriched
    return profile


def build_ioc_event_timeline(db_path: Path, limit: int = 100) -> dict[str, Any]:
    """Build a JSON-safe M18 IOC event timeline from the local SQLite history."""
    capped_limit = max(1, min(int(limit), 500))
    if not db_path.is_file():
        return {
            "schema_version": "m18.ioc_timeline.v1",
            "db_path": db_path.as_posix(),
            "event_count": 0,
            "events": [],
            "source": "sqlite_ioc_history",
        }
    _init_ioc_db(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM ioc_history ORDER BY last_seen DESC, confidence_score DESC, ioc_type, value").fetchall()
    events: list[dict[str, Any]] = []
    for row in rows:
        sources = json.loads(str(row["sources_json"]))
        base = {
            "ioc_id": row["ioc_id"],
            "ioc_type": row["ioc_type"],
            "value": row["value"],
            "observation_count": int(row["observation_count"]),
            "source_count": len(sources),
            "sources": sources,
            "confidence_score": float(row["confidence_score"]),
            "confidence_level": row["confidence_level"],
            "ip_scope": row["ip_scope"],
        }
        events.append({"event_type": "ioc_first_seen", "timestamp": row["first_seen"], **base})
        if row["last_seen"] != row["first_seen"]:
            events.append({"event_type": "ioc_last_seen", "timestamp": row["last_seen"], **base})
    events.sort(key=lambda item: (str(item["timestamp"]), str(item["event_type"]), str(item["ioc_type"]), str(item["value"])), reverse=True)
    selected = events[:capped_limit]
    return {
        "schema_version": "m18.ioc_timeline.v1",
        "db_path": db_path.as_posix(),
        "event_count": len(selected),
        "total_event_count": len(events),
        "events": selected,
        "source": "sqlite_ioc_history",
    }

def _compose_for(profile: str, listen_host: str) -> dict[str, Any]:
    if profile == "ssh":
        return {"image": "cowrie/cowrie:latest", "ports": [f"{listen_host}:2222:2222"], "read_only": True}
    if profile == "http":
        return {"image": "nginxinc/nginx-unprivileged:stable-alpine", "ports": [f"{listen_host}:8080:8080"], "read_only": True}
    return {"image": "alpine/socat:latest", "command": "-dd TCP-LISTEN:2323,fork,reuseaddr SYSTEM:'echo deception-canary'", "ports": [f"{listen_host}:2323:2323"], "read_only": True}


@dataclass(frozen=True, slots=True)
class DeploymentBundle:
    bundle_path: Path
    profiles: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {"bundle_path": str(self.bundle_path), "profiles": self.profiles, "service_count": len(self.profiles)}


class HoneypotDeploymentBundleTechnique(BaseTechnique):
    technique_id = "deception.defensive.prepare_honeypot_bundle"
    module_id = M18_MODULE_ID
    display_name = "Prepare defensive honeypot deployment bundle"
    description = "Create isolated honeypot deployment artifacts for operator review without launching services."
    tool_name = "internal_honeypot_bundle_builder"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["output_dir", "profiles", "listen_host", "retention_days"]
    expected_evidence = ["deployment_bundle", "isolation_controls"]
    input_schema = {"output_dir": {"type": "string"}, "profiles": {"type": "array"}, "listen_host": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "profiles", "label": "Honeypot profiles", "type": "multiselect"}]
    success_markers = ["deployment_bundle"]
    failure_markers = ["invalid_profile", "invalid_output_dir"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"deployment_bundle": "dict", "isolation_controls": "dict"}
    version_lock_id = "m18_honeypots/defensive-bundle-builder"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        output_dir = Path(str(context.parameters.get("output_dir") or "storage/workspaces/m18_honeypots_deception/bundles")).resolve()
        profiles = _profile_list(context.parameters.get("profiles"))
        listen_host = str(context.parameters.get("listen_host") or "127.0.0.1").strip()
        if _valid_ip(listen_host) is None:
            raise ContractError("listen_host must be a valid IP address.")
        retention_days = int(context.parameters.get("retention_days") or 14)
        if not 1 <= retention_days <= 365:
            raise ContractError("retention_days must be between 1 and 365.")
        bundle_path = output_dir / _safe_name(context.run_id, "run_id")
        (bundle_path / "config").mkdir(parents=True, exist_ok=True)
        services = {f"m18-{profile}": _compose_for(profile, listen_host) for profile in profiles}
        compose = {"version": "3.9", "services": services, "networks": {"m18-deception": {"internal": True}}}
        (bundle_path / "docker-compose.yml").write_text(json.dumps(compose, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        controls = {
            "auto_start": False,
            "network_internal": True,
            "listen_host": listen_host,
            "retention_days": retention_days,
            "secrets_expected": False,
            "operator_review_required_before_launch": True,
            "countermeasures_enabled": False,
        }
        (bundle_path / "config" / "controls.json").write_text(json.dumps(controls, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        bundle = DeploymentBundle(bundle_path=bundle_path, profiles=profiles)
        content = {"deployment_bundle": bundle.to_dict(), "isolation_controls": controls, "services_started": False, "mutation_performed": False}
        evidence = _evidence(context, self.technique_id, "honeypot_deployment_bundle", "Defensive honeypot deployment bundle prepared for operator review.", content)
        return TechniqueExecutionResult(self.technique_id, M18_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class HoneypotIocExtractionTechnique(BaseTechnique):
    technique_id = "deception.defensive.extract_iocs"
    module_id = M18_MODULE_ID
    display_name = "Extract IOCs from honeypot logs"
    description = "Parse supplied honeypot logs and extract IPs, URLs, hashes, usernames, HTTP paths and user agents."
    tool_name = "internal_honeypot_ioc_parser"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["log_json", "log_path"]
    expected_evidence = ["ioc_summary", "normalized_events"]
    input_schema = {"log_json": {"type": "object"}, "log_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "log_json", "label": "Honeypot log JSON or lines", "type": "textarea"}]
    success_markers = ["ioc_summary"]
    failure_markers = ["invalid_log"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"ioc_summary": "dict", "normalized_events": "list"}
    version_lock_id = "m18_honeypots/ioc-extraction"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        events = _line_events(_read_json_or_lines(context.parameters, "log_json", "log_path"))
        iocs = _extract_iocs(events)
        content = {"ioc_summary": iocs, "normalized_events": events, "remote_collection_performed": False, "countermeasure_performed": False}
        evidence = _evidence(context, self.technique_id, "honeypot_iocs", "Honeypot IOCs extracted from supplied logs.", content)
        return TechniqueExecutionResult(self.technique_id, M18_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class PassiveIntrusionProfilingTechnique(BaseTechnique):
    technique_id = "deception.defensive.passive_intrusion_profile"
    module_id = M18_MODULE_ID
    display_name = "Passive intrusion profiling"
    description = "Build passive actor profiles from supplied honeypot events without interacting with the actor."
    tool_name = "internal_passive_intrusion_profiler"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["log_json", "log_path"]
    expected_evidence = ["intrusion_profiles", "normalized_events"]
    input_schema = {"log_json": {"type": "object"}, "log_path": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "log_json", "label": "Honeypot event JSON or lines", "type": "textarea"}]
    success_markers = ["actor_profiles"]
    failure_markers = ["invalid_log"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"intrusion_profiles": "dict", "normalized_events": "list"}
    version_lock_id = "m18_honeypots/passive-intrusion-profiler"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        events = _line_events(_read_json_or_lines(context.parameters, "log_json", "log_path"))
        profile = _profile_events(events)
        content = {"intrusion_profiles": profile, "normalized_events": events, "remote_collection_performed": False, "countermeasure_performed": False}
        evidence = _evidence(context, self.technique_id, "passive_intrusion_profile", "Passive honeypot intrusion profile built from supplied logs.", content, quality=EVIDENCE_QUALITY_MEDIUM)
        return TechniqueExecutionResult(self.technique_id, M18_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)


class HistoricalIocScoringTechnique(BaseTechnique):
    technique_id = "deception.defensive.historical_ioc_scoring"
    module_id = M18_MODULE_ID
    display_name = "Persist historical IOCs with confidence scoring"
    description = "Persist operator-supplied honeypot IOCs to SQLite and compute passive confidence scores without contacting infrastructure."
    tool_name = "internal_historical_ioc_store"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "PythonToolWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "none"
    required_inputs = []
    optional_inputs = ["log_json", "log_path", "db_path", "source"]
    expected_evidence = ["historical_ioc_inventory", "passive_actor_profiles"]
    input_schema = {"log_json": {"type": "object"}, "log_path": {"type": "string"}, "db_path": {"type": "string"}, "source": {"type": "string"}}
    ai_fillable_inputs = []
    panel_fields = [{"name": "log_json", "label": "Honeypot event JSON or lines", "type": "textarea"}]
    success_markers = ["historical_ioc_inventory"]
    failure_markers = ["invalid_log", "invalid_db_path"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"historical_ioc_inventory": "dict", "passive_actor_profiles": "dict"}
    version_lock_id = "m18_honeypots/historical-ioc-scoring"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        events = _line_events(_read_json_or_lines(context.parameters, "log_json", "log_path"))
        iocs = _extract_iocs(events)
        source = _safe_name(context.parameters.get("source") or "operator-supplied", "source")
        db_path = Path(str(context.parameters.get("db_path") or "storage/workspaces/m18_honeypots_deception/ioc_history.sqlite3")).resolve()
        rows = _ioc_rows_from_summary(iocs, events, source)
        inventory = persist_ioc_history(db_path, rows)
        actor_profiles = _actor_confidence_profiles(events)
        content = {
            "historical_ioc_inventory": inventory,
            "passive_actor_profiles": actor_profiles,
            "normalized_events": events,
            "remote_collection_performed": False,
            "countermeasure_performed": False,
            "scoring_model": "deterministic-passive-confidence-v1",
        }
        evidence = _evidence(context, self.technique_id, "historical_ioc_scoring", "Historical honeypot IOCs persisted and passively scored.", content, quality=EVIDENCE_QUALITY_MEDIUM)
        return TechniqueExecutionResult(self.technique_id, M18_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], content)
