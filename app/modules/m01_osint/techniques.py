"""Concrete M01 OSINT techniques 1-47.

The techniques in this module execute only operator-supplied targets through
explicit command arguments. They never use a shell, never expand target ranges
internally, and support dry-run through the shared worker contract before
``execute`` is reached.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import hashlib
from datetime import UTC, datetime
import socket
from dataclasses import dataclass
from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Any

import requests

from app.contracts.evidence_contract import (
    EVIDENCE_QUALITY_HIGH,
    EVIDENCE_QUALITY_MEDIUM,
    EvidenceRecord,
    RESULT_MISSING_TOOL,
    RESULT_SUCCESS,
)
from app.contracts.technique_contract import (
    BaseTechnique,
    STATUS_READY_CONTROLLED,
    TechniqueExecutionContext,
    TechniqueExecutionResult,
)
from app.core.errors import ContractError
from app.core.technique_evidence_utils import stable_evidence_id, utc_now_iso
from app.core.permission_levels import PERMISSION_ACTIVE_LOW
from app.core.permission_levels import PERMISSION_PASSIVE
from app.core.secret_store import DEFAULT_SECRET_STORE

M01_MODULE_ID = "m01_osint"
DEFAULT_TIMEOUT_SECONDS = 120


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Completed external command result captured without invoking a shell."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False
    cache_status: str = "miss"

    def to_dict(self) -> dict[str, object]:
        return {
            "command": list(self.command),
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "timed_out": self.timed_out,
            "cache_status": self.cache_status,
        }


def _require_string(parameters: dict[str, Any], name: str) -> str:
    value = str(parameters.get(name, "")).strip()
    if not value:
        raise ContractError(f"{name} is required.")
    return value


def _ensure_confirmed(context: TechniqueExecutionContext) -> None:
    if not context.confirmed:
        raise ContractError("Controlled M01 active discovery requires explicit operator confirmation.")


def _optional_int(parameters: dict[str, Any], name: str, default: int, minimum: int, maximum: int) -> int:
    raw_value = parameters.get(name, default)
    if isinstance(raw_value, bool):
        raise ContractError(f"{name} must be an integer.")
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as error:
        raise ContractError(f"{name} must be an integer.") from error
    if value < minimum or value > maximum:
        raise ContractError(f"{name} must be between {minimum} and {maximum}.")
    return value


def _optional_bool(parameters: dict[str, Any], name: str, default: bool) -> bool:
    raw_value = parameters.get(name, default)
    if isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, str):
        normalized = raw_value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    raise ContractError(f"{name} must be a boolean.")


def _choice(parameters: dict[str, Any], name: str, default: str, allowed: set[str]) -> str:
    value = str(parameters.get(name, default)).strip().lower()
    if value not in allowed:
        raise ContractError(f"{name} must be one of: {', '.join(sorted(allowed))}.")
    return value


def _validate_target(value: str) -> str:
    target = value.strip().lower().rstrip(".")
    if not target:
        raise ContractError("target is required.")
    if target.startswith(("http://", "https://")) or "/" in target and not _is_network(target):
        raise ContractError("target must be a domain, IP address, or CIDR range, not a URL/path.")
    if _is_ip(target) or _is_network(target):
        return target
    labels = target.split(".")
    if any(not label or len(label) > 63 for label in labels):
        raise ContractError("target domain labels are invalid.")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-")
    if any(label.startswith("-") or label.endswith("-") or any(char not in allowed for char in label) for label in labels):
        raise ContractError("target domain contains invalid characters.")
    return target


def _is_ip(value: str) -> bool:
    try:
        ip_address(value)
    except ValueError:
        return False
    return True


def _is_network(value: str) -> bool:
    try:
        ip_network(value, strict=False)
    except ValueError:
        return False
    return "/" in value


def _ports_arg(value: str) -> str:
    ports = value.strip()
    if not ports:
        raise ContractError("ports is required.")
    allowed = set("0123456789,-UT:")
    if any(char not in allowed for char in ports):
        raise ContractError("ports contains unsupported characters.")
    return ports


def _domain_arg(parameters: dict[str, Any], name: str = "domain") -> str:
    domain = _validate_target(_require_string(parameters, name))
    if _is_ip(domain) or _is_network(domain):
        raise ContractError(f"{name} must be a domain.")
    return domain


def _string_list(parameters: dict[str, Any], name: str) -> list[str]:
    raw_value = parameters.get(name, [])
    if isinstance(raw_value, str):
        values = [line.strip() for line in raw_value.replace(",", "\n").splitlines()]
    elif isinstance(raw_value, list):
        values = [str(item).strip() for item in raw_value]
    else:
        raise ContractError(f"{name} must be a list of strings.")
    return [value for value in values if value]


def _api_key(parameters: dict[str, Any], env_names: tuple[str, ...], parameter_name: str = "api_key") -> str:
    explicit = str(parameters.get(parameter_name, "")).strip()
    if explicit:
        raise ContractError(f"{parameter_name} must be configured through the secure secret store or runtime environment, not inline parameters.")
    lookup = DEFAULT_SECRET_STORE.get_secret(env_names[0], env_names)
    if lookup.status == "available" and lookup.value:
        return lookup.value
    raise ContractError(f"Missing API key. Configure secure secret {env_names[0]} or one of: {', '.join(env_names)}. Status: {lookup.status}.")


def _http_get_json(url: str, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None, timeout_seconds: int = 20) -> dict[str, Any]:
    response = requests.get(url, headers=headers or {}, params=params or {}, timeout=timeout_seconds)
    payload: Any
    try:
        payload = response.json()
    except ValueError as error:
        raise ContractError(f"API response from {url} was not valid JSON.") from error
    if not isinstance(payload, dict):
        raise ContractError(f"API response from {url} must be a JSON object.")
    return {
        "status_code": response.status_code,
        "url": response.url,
        "payload": payload,
    }


def _tool_path(tool_name: str) -> str | None:
    return shutil.which(tool_name)


def _cache_enabled() -> bool:
    return os.environ.get("OJO_M01_DISABLE_CACHE", "").strip().lower() not in {"1", "true", "yes", "on"}


def _cache_base_path() -> Path:
    return Path(os.environ.get("OJO_M01_CACHE_DIR", "storage/cache/m01_osint"))


def _command_cache_key(command: list[str], timeout_seconds: int, stdin: str | None) -> str:
    payload = {"command": command, "stdin": stdin or "", "timeout_seconds": timeout_seconds}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _read_cached_command(cache_path: Path, command: list[str]) -> CommandResult | None:
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return CommandResult(
        command=tuple(command),
        returncode=int(payload.get("returncode", 1)),
        stdout=str(payload.get("stdout", "")),
        stderr=str(payload.get("stderr", "")),
        timed_out=bool(payload.get("timed_out", False)),
        cache_status="hit",
    )


def _write_cached_command(cache_path: Path, result: CommandResult) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_dict() | {"cached_at": datetime.now(UTC).isoformat()}
    temporary_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
    temporary_path.write_text(json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary_path.replace(cache_path)


def _run_command(command: list[str], timeout_seconds: int, stdin: str | None = None) -> CommandResult:
    cache_path = _cache_base_path() / f"{_command_cache_key(command, timeout_seconds, stdin)}.json"
    if _cache_enabled():
        cached = _read_cached_command(cache_path, command)
        if cached is not None:
            return cached
    try:
        completed = subprocess.run(
            command,
            input=stdin,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        result = CommandResult(
            command=tuple(command),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
            cache_status="miss",
        )
    except subprocess.TimeoutExpired as error:
        result = CommandResult(
            command=tuple(command),
            returncode=124,
            stdout=str(error.stdout or ""),
            stderr=str(error.stderr or "") + f"\ncommand timed out after {timeout_seconds} second(s)",
            timed_out=True,
            cache_status="miss",
        )
    if _cache_enabled():
        _write_cached_command(cache_path, result)
    return result


def _json_lines(text: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            items.append(parsed)
    return items


def _text_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _execution_evidence(
    context: TechniqueExecutionContext,
    technique_id: str,
    evidence_type: str,
    quality: str,
    summary: str,
    content: dict[str, Any],
    source: str,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_id=stable_evidence_id(context.run_id, technique_id, evidence_type),
        run_id=context.run_id,
        target_id=context.target_id,
        technique_id=technique_id,
        module_id=M01_MODULE_ID,
        evidence_type=evidence_type,
        quality=quality,
        summary=summary,
        content=content,
        source=source,
        demo=False,
        real_execution=True,
        created_at=utc_now_iso(),
    )


def _missing_tool_result(technique_id: str, tool_names: list[str]) -> TechniqueExecutionResult:
    return TechniqueExecutionResult(
        technique_id=technique_id,
        module_id=M01_MODULE_ID,
        result_status=RESULT_MISSING_TOOL,
        summary=f"Missing required tool(s): {', '.join(tool_names)}.",
        raw_result={"missing_tools": tool_names, "real_execution": False},
        error=f"Missing required tool(s): {', '.join(tool_names)}.",
    )


class NmapTcpUdpMassiveTechnique(BaseTechnique):
    """Technique 1: controlled Nmap TCP/UDP surface discovery."""

    technique_id = "osint.nmap_tcp_udp_massive"
    module_id = M01_MODULE_ID
    display_name = "Nmap TCP/UDP massive discovery"
    description = "Controlled Nmap TCP/UDP discovery for authorized targets."
    tool_name = "Nmap + Npcap"
    recommended_version = "Nmap 7.99 + Npcap 1.88"
    runtime = "windows"
    worker = "windows"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "medium"
    required_inputs = ["target", "ports"]
    optional_inputs = ["protocol_mode", "scan_profile", "timing_profile", "output_format", "max_duration_seconds"]
    expected_evidence = ["open_ports", "service_fingerprints", "normalized_json", "attack_surface_updates"]
    input_schema = {
        "target": {"type": "string"},
        "ports": {"type": "string"},
        "protocol_mode": {"enum": ["tcp", "udp", "both"]},
        "scan_profile": {"enum": ["quick", "standard", "deep", "custom"]},
        "timing_profile": {"enum": ["low_noise", "normal", "fast", "custom"]},
        "output_format": {"enum": ["json", "xml", "text"]},
        "max_duration_seconds": {"type": "integer", "minimum": 5, "maximum": 3600},
    }
    ai_fillable_inputs = ["ports", "protocol_mode", "scan_profile", "timing_profile"]
    panel_fields = [
        {"name": "target", "label": "Target", "type": "text"},
        {"name": "ports", "label": "Ports", "type": "text"},
        {"name": "protocol_mode", "label": "Protocol mode", "type": "select"},
        {"name": "scan_profile", "label": "Scan profile", "type": "select"},
    ]
    success_markers = ["open_ports", "service_fingerprints"]
    failure_markers = ["missing_nmap", "nmap_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True, "build_command": True}
    requires_allowlisted_target = True
    requires_network = True
    configurable_parameters = {"safe_subprocess": True, "shell": False}
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    can_run_in_demo = True
    can_run_in_dry_run = True
    evidence_schema = {"open_ports": "list", "service_fingerprints": "list", "attack_surface_updates": "list"}
    version_lock_id = "m01_osint/nmap"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_confirmed(context)
        target = _validate_target(_require_string(context.parameters, "target"))
        ports = _ports_arg(_require_string(context.parameters, "ports"))
        protocol_mode = _choice(context.parameters, "protocol_mode", "tcp", {"tcp", "udp", "both"})
        scan_profile = _choice(context.parameters, "scan_profile", "standard", {"quick", "standard", "deep", "custom"})
        timing_profile = _choice(context.parameters, "timing_profile", "low_noise", {"low_noise", "normal", "fast", "custom"})
        timeout = _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600)
        nmap_path = _tool_path("nmap")
        if nmap_path is None:
            return _missing_tool_result(self.technique_id, ["nmap"])
        command = [nmap_path, "-oX", "-", "-p", ports]
        if protocol_mode in {"udp", "both"}:
            command.append("-sU")
        if protocol_mode in {"tcp", "both"}:
            command.append("-sT")
        command.extend(_nmap_profile_args(scan_profile, timing_profile))
        command.append(target)
        result = _run_command(command, timeout)
        open_ports = _parse_nmap_xml_ports(result.stdout)
        evidence = _execution_evidence(
            context,
            self.technique_id,
            "nmap_xml_result",
            EVIDENCE_QUALITY_HIGH if open_ports else EVIDENCE_QUALITY_MEDIUM,
            f"Nmap completed with {len(open_ports)} open port(s) parsed.",
            {
                "target": target,
                "command": list(result.command),
                "returncode": result.returncode,
                "open_ports": open_ports,
                "service_fingerprints": open_ports,
                "attack_surface_updates": _port_graph_updates(target, open_ports),
                "stderr": result.stderr,
                "started_by_confirmed_operator": context.confirmed,
            },
            "nmap",
        )
        return TechniqueExecutionResult(
            technique_id=self.technique_id,
            module_id=M01_MODULE_ID,
            result_status=RESULT_SUCCESS,
            summary=evidence.summary,
            evidence=[evidence],
            raw_result=result.to_dict() | {"open_ports": open_ports},
        )


class MasscanFastSweepTechnique(BaseTechnique):
    """Technique 2: controlled masscan fast sweep."""

    technique_id = "osint.masscan_fast_sweep"
    module_id = M01_MODULE_ID
    display_name = "masscan fast sweep"
    description = "Controlled masscan sweep for authorized targets."
    tool_name = "masscan"
    recommended_version = "1.3.2"
    runtime = "windows_or_wsl2"
    worker = "wsl"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "medium"
    required_inputs = ["target", "ports"]
    optional_inputs = ["rate_profile", "interface", "output_format", "max_duration_seconds"]
    expected_evidence = ["open_ports", "normalized_json", "attack_surface_updates"]
    input_schema = {
        "target": {"type": "string"},
        "ports": {"type": "string"},
        "rate_profile": {"enum": ["low", "normal", "fast", "custom"]},
        "interface": {"type": "string"},
        "output_format": {"enum": ["json", "list", "text"]},
        "max_duration_seconds": {"type": "integer", "minimum": 5, "maximum": 3600},
    }
    ai_fillable_inputs = ["ports", "rate_profile"]
    panel_fields = [
        {"name": "target", "label": "Target", "type": "text"},
        {"name": "ports", "label": "Ports", "type": "text"},
        {"name": "rate_profile", "label": "Rate profile", "type": "select"},
    ]
    success_markers = ["open_ports"]
    failure_markers = ["missing_masscan", "masscan_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True, "build_command": True}
    requires_allowlisted_target = True
    requires_network = True
    configurable_parameters = {"safe_subprocess": True, "shell": False}
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    can_run_in_demo = True
    can_run_in_dry_run = True
    evidence_schema = {"open_ports": "list", "attack_surface_updates": "list"}
    version_lock_id = "m01_osint/masscan"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_confirmed(context)
        target = _validate_target(_require_string(context.parameters, "target"))
        ports = _ports_arg(_require_string(context.parameters, "ports"))
        rate_profile = _choice(context.parameters, "rate_profile", "low", {"low", "normal", "fast", "custom"})
        timeout = _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600)
        masscan_path = _tool_path("masscan")
        if masscan_path is None:
            return _missing_tool_result(self.technique_id, ["masscan"])
        command = [masscan_path, target, "-p", ports, "--rate", str(_masscan_rate(rate_profile)), "--output-format", "json", "--output-filename", "-"]
        interface = str(context.parameters.get("interface", "")).strip()
        if interface:
            command.extend(["--adapter", interface])
        result = _run_command(command, timeout)
        open_ports = _parse_masscan_json_ports(result.stdout)
        evidence = _execution_evidence(
            context,
            self.technique_id,
            "masscan_json_result",
            EVIDENCE_QUALITY_HIGH if open_ports else EVIDENCE_QUALITY_MEDIUM,
            f"masscan completed with {len(open_ports)} open port(s) parsed.",
            {
                "target": target,
                "command": list(result.command),
                "returncode": result.returncode,
                "open_ports": open_ports,
                "attack_surface_updates": _port_graph_updates(target, open_ports),
                "stderr": result.stderr,
                "started_by_confirmed_operator": context.confirmed,
            },
            "masscan",
        )
        return TechniqueExecutionResult(
            technique_id=self.technique_id,
            module_id=M01_MODULE_ID,
            result_status=RESULT_SUCCESS,
            summary=evidence.summary,
            evidence=[evidence],
            raw_result=result.to_dict() | {"open_ports": open_ports},
        )


class NaabuHttpxKatanaDiscoveryTechnique(BaseTechnique):
    """Technique 3: controlled Naabu + httpx + Katana web discovery pipeline."""

    technique_id = "osint.naabu_httpx_katana_discovery"
    module_id = M01_MODULE_ID
    display_name = "Naabu httpx Katana discovery"
    description = "Controlled Naabu, httpx and Katana discovery for authorized web surfaces."
    tool_name = "Naabu + httpx + Katana"
    recommended_version = "Naabu 2.x + httpx 1.9.0 + Katana 1.6.x"
    runtime = "windows"
    worker = "windows"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "medium"
    required_inputs = ["target"]
    optional_inputs = [
        "port_profile",
        "http_probe_enabled",
        "crawl_enabled",
        "crawl_depth",
        "include_headers",
        "include_technologies",
        "output_format",
    ]
    expected_evidence = [
        "web_services",
        "http_headers",
        "crawled_urls",
        "discovered_endpoints",
        "technology_hints",
        "normalized_json",
        "attack_surface_updates",
    ]
    input_schema = {
        "target": {"type": "string"},
        "port_profile": {"enum": ["top", "web", "custom"]},
        "http_probe_enabled": {"type": "boolean"},
        "crawl_enabled": {"type": "boolean"},
        "crawl_depth": {"type": "integer", "minimum": 0, "maximum": 5},
        "include_headers": {"type": "boolean"},
        "include_technologies": {"type": "boolean"},
        "output_format": {"enum": ["json", "report"]},
    }
    ai_fillable_inputs = ["port_profile", "crawl_depth", "include_headers", "include_technologies"]
    panel_fields = [
        {"name": "target", "label": "Target", "type": "text"},
        {"name": "port_profile", "label": "Port profile", "type": "select"},
        {"name": "http_probe_enabled", "label": "HTTP probe", "type": "checkbox"},
        {"name": "crawl_enabled", "label": "Crawl", "type": "checkbox"},
    ]
    success_markers = ["web_services", "discovered_endpoints"]
    failure_markers = ["missing_naabu", "missing_httpx", "missing_katana"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True, "build_command": True}
    requires_allowlisted_target = True
    requires_network = True
    configurable_parameters = {"safe_subprocess": True, "shell": False}
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    can_run_in_demo = True
    can_run_in_dry_run = True
    evidence_schema = {"web_services": "list", "crawled_urls": "list", "technology_hints": "list"}
    version_lock_id = "m01_osint/naabu-httpx-katana"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_confirmed(context)
        target = _validate_target(_require_string(context.parameters, "target"))
        port_profile = _choice(context.parameters, "port_profile", "web", {"top", "web", "custom"})
        http_probe_enabled = _optional_bool(context.parameters, "http_probe_enabled", True)
        crawl_enabled = _optional_bool(context.parameters, "crawl_enabled", True)
        crawl_depth = _optional_int(context.parameters, "crawl_depth", 1, 0, 5)
        include_headers = _optional_bool(context.parameters, "include_headers", True)
        include_technologies = _optional_bool(context.parameters, "include_technologies", True)
        timeout = _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600)
        missing = [tool for tool in ("naabu",) if _tool_path(tool) is None]
        if http_probe_enabled and _tool_path("httpx") is None:
            missing.append("httpx")
        if crawl_enabled and _tool_path("katana") is None:
            missing.append("katana")
        if missing:
            return _missing_tool_result(self.technique_id, missing)

        naabu_command = [_tool_path("naabu") or "naabu", "-host", target, "-json", "-silent"]
        if port_profile == "web":
            naabu_command.extend(["-p", "80,443,8080,8443"])
        naabu_result = _run_command(naabu_command, timeout)
        naabu_services = _parse_naabu_json_services(naabu_result.stdout, target)
        urls = _urls_from_services(naabu_services)
        httpx_result: CommandResult | None = None
        web_services: list[dict[str, Any]] = []
        if http_probe_enabled and urls:
            httpx_command = [_tool_path("httpx") or "httpx", "-json", "-silent"]
            if include_headers:
                httpx_command.append("-include-response-header")
            if include_technologies:
                httpx_command.append("-tech-detect")
            httpx_result = _run_command(httpx_command, timeout, stdin="\n".join(urls) + "\n")
            web_services = _parse_httpx_json_services(httpx_result.stdout)
        katana_result: CommandResult | None = None
        crawled_urls: list[str] = []
        if crawl_enabled and urls and crawl_depth > 0:
            katana_command = [_tool_path("katana") or "katana", "-json", "-silent", "-d", str(crawl_depth)]
            katana_result = _run_command(katana_command, timeout, stdin="\n".join(urls) + "\n")
            crawled_urls = _parse_katana_urls(katana_result.stdout)
        evidence = _execution_evidence(
            context,
            self.technique_id,
            "web_discovery_json_result",
            EVIDENCE_QUALITY_HIGH if web_services or crawled_urls else EVIDENCE_QUALITY_MEDIUM,
            f"Naabu/httpx/Katana pipeline completed with {len(web_services)} web service(s) and {len(crawled_urls)} crawled URL(s).",
            {
                "target": target,
                "commands": {
                    "naabu": list(naabu_result.command),
                    "httpx": list(httpx_result.command) if httpx_result else None,
                    "katana": list(katana_result.command) if katana_result else None,
                },
                "returncodes": {
                    "naabu": naabu_result.returncode,
                    "httpx": httpx_result.returncode if httpx_result else None,
                    "katana": katana_result.returncode if katana_result else None,
                },
                "web_services": web_services,
                "crawled_urls": crawled_urls,
                "discovered_endpoints": sorted(set(urls + crawled_urls)),
                "technology_hints": _technology_hints(web_services),
                "attack_surface_updates": _web_graph_updates(target, web_services, crawled_urls),
                "stderr": {
                    "naabu": naabu_result.stderr,
                    "httpx": httpx_result.stderr if httpx_result else None,
                    "katana": katana_result.stderr if katana_result else None,
                },
                "started_by_confirmed_operator": context.confirmed,
            },
            "naabu-httpx-katana",
        )
        return TechniqueExecutionResult(
            technique_id=self.technique_id,
            module_id=M01_MODULE_ID,
            result_status=RESULT_SUCCESS,
            summary=evidence.summary,
            evidence=[evidence],
            raw_result={"naabu": naabu_result.to_dict(), "httpx": httpx_result.to_dict() if httpx_result else None, "katana": katana_result.to_dict() if katana_result else None},
        )


class SubfinderSubdomainEnumTechnique(BaseTechnique):
    """Technique 4: passive Subfinder subdomain enumeration."""

    technique_id = "osint.subfinder_subdomain_enum"
    module_id = M01_MODULE_ID
    display_name = "Subfinder subdomain enumeration"
    description = "Passive subdomain enumeration with Subfinder for an authorized domain."
    tool_name = "Subfinder"
    recommended_version = "2.14.0"
    runtime = "windows"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["domain"]
    optional_inputs = ["source_profile", "recursive", "include_resolved", "output_format"]
    expected_evidence = ["subdomains", "source_urls", "normalized_json", "attack_surface_updates"]
    input_schema = {"domain": {"type": "string"}, "recursive": {"type": "boolean"}, "include_resolved": {"type": "boolean"}}
    ai_fillable_inputs = ["source_profile", "recursive", "include_resolved"]
    panel_fields = [{"name": "domain", "label": "Domain", "type": "text"}]
    success_markers = ["subdomains"]
    failure_markers = ["missing_subfinder", "subfinder_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True, "build_command": True}
    requires_network = True
    configurable_parameters = {"safe_subprocess": True, "shell": False}
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"subdomains": "list", "attack_surface_updates": "list"}
    version_lock_id = "m01_osint/subfinder"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        domain = _domain_arg(context.parameters)
        recursive = _optional_bool(context.parameters, "recursive", False)
        timeout = _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600)
        subfinder_path = _tool_path("subfinder")
        if subfinder_path is None:
            return _missing_tool_result(self.technique_id, ["subfinder"])
        command = [subfinder_path, "-d", domain, "-json", "-silent"]
        if recursive:
            command.append("-recursive")
        result = _run_command(command, timeout)
        subdomains = _parse_subfinder_domains(result.stdout, domain)
        evidence = _execution_evidence(
            context,
            self.technique_id,
            "subfinder_json_result",
            EVIDENCE_QUALITY_HIGH if subdomains else EVIDENCE_QUALITY_MEDIUM,
            f"Subfinder completed with {len(subdomains)} subdomain(s).",
            {
                "domain": domain,
                "command": list(result.command),
                "returncode": result.returncode,
                "subdomains": subdomains,
                "source_urls": ["https://github.com/projectdiscovery/subfinder"],
                "attack_surface_updates": _domain_graph_updates(domain, subdomains),
                "stderr": result.stderr,
            },
            "subfinder",
        )
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], result.to_dict() | {"subdomains": subdomains})


class AmassPassiveActiveEnumTechnique(BaseTechnique):
    """Technique 5: Amass passive or explicitly confirmed active enumeration."""

    technique_id = "osint.amass_passive_active_enum"
    module_id = M01_MODULE_ID
    display_name = "Amass passive/active enumeration"
    description = "Amass domain enumeration with passive mode by default and active mode only after explicit confirmation."
    tool_name = "Amass"
    recommended_version = "latest-release-lock"
    runtime = "windows"
    worker = "windows"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "medium"
    required_inputs = ["domain"]
    optional_inputs = ["mode", "source_profile", "include_asn", "include_ips", "max_duration_seconds", "output_format"]
    expected_evidence = ["subdomains", "ips", "asn_records", "graph_edges", "normalized_json", "attack_surface_updates"]
    input_schema = {"domain": {"type": "string"}, "mode": {"enum": ["passive", "active", "both"]}}
    ai_fillable_inputs = ["mode", "include_asn", "include_ips"]
    panel_fields = [{"name": "domain", "label": "Domain", "type": "text"}, {"name": "mode", "label": "Mode", "type": "select"}]
    success_markers = ["subdomains", "graph_edges"]
    failure_markers = ["missing_amass", "amass_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True, "build_command": True}
    requires_allowlisted_target = True
    requires_network = True
    configurable_parameters = {"safe_subprocess": True, "shell": False}
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"subdomains": "list", "ips": "list", "asn_records": "list", "graph_edges": "list"}
    version_lock_id = "m01_osint/amass"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        domain = _domain_arg(context.parameters)
        mode = _choice(context.parameters, "mode", "passive", {"passive", "active", "both"})
        if mode in {"active", "both"}:
            _ensure_confirmed(context)
        timeout = _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600)
        amass_path = _tool_path("amass")
        if amass_path is None:
            return _missing_tool_result(self.technique_id, ["amass"])
        command = [amass_path, "enum", "-d", domain, "-json", "-"]
        if mode == "passive":
            command.append("-passive")
        result = _run_command(command, timeout)
        parsed = _parse_amass_json(result.stdout, domain)
        evidence = _execution_evidence(
            context,
            self.technique_id,
            "amass_json_result",
            EVIDENCE_QUALITY_HIGH if parsed["subdomains"] else EVIDENCE_QUALITY_MEDIUM,
            f"Amass completed in {mode} mode with {len(parsed['subdomains'])} subdomain(s).",
            {
                "domain": domain,
                "mode": mode,
                "command": list(result.command),
                "returncode": result.returncode,
                **parsed,
                "attack_surface_updates": _domain_graph_updates(domain, parsed["subdomains"]),
                "stderr": result.stderr,
            },
            "amass",
        )
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], result.to_dict() | parsed)


class AquatoneScreenshotsTechnique(BaseTechnique):
    """Technique 6: Aquatone screenshots for operator-provided URLs."""

    technique_id = "osint.aquatone_screenshots"
    module_id = M01_MODULE_ID
    display_name = "Aquatone screenshots"
    description = "Capture visual evidence for operator-provided URLs using Aquatone."
    tool_name = "Aquatone"
    recommended_version = "latest-release-lock / v1.7.0 baseline"
    runtime = "windows_or_wsl2"
    worker = "wsl"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["urls"]
    optional_inputs = ["targets_file", "screenshot_profile", "output_directory", "include_html_report"]
    expected_evidence = ["screenshots", "html_report_path", "screenshot_hashes", "normalized_json"]
    input_schema = {"urls": {"type": "array"}, "output_directory": {"type": "string"}}
    ai_fillable_inputs = ["screenshot_profile", "include_html_report"]
    panel_fields = [{"name": "urls", "label": "URLs", "type": "textarea"}]
    success_markers = ["screenshots", "html_report_path"]
    failure_markers = ["missing_aquatone", "aquatone_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True, "build_command": True}
    requires_allowlisted_target = True
    requires_network = True
    configurable_parameters = {"safe_subprocess": True, "shell": False}
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"screenshots": "list", "screenshot_hashes": "list"}
    version_lock_id = "m01_osint/aquatone"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_confirmed(context)
        urls = _string_list(context.parameters, "urls")
        if not urls:
            raise ContractError("urls must include at least one URL.")
        if any(not url.startswith(("http://", "https://")) for url in urls):
            raise ContractError("urls must contain only http or https URLs.")
        timeout = _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600)
        aquatone_path = _tool_path("aquatone")
        if aquatone_path is None:
            return _missing_tool_result(self.technique_id, ["aquatone"])
        output_directory = Path(str(context.parameters.get("output_directory") or f"storage/workspaces/{M01_MODULE_ID}/aquatone/{context.run_id}"))
        command = [aquatone_path, "-out", output_directory.as_posix()]
        result = _run_command(command, timeout, stdin="\n".join(urls) + "\n")
        screenshots = _collect_file_hashes(output_directory, {".png", ".jpg", ".jpeg"})
        html_report = output_directory / "aquatone_report.html"
        evidence = _execution_evidence(
            context,
            self.technique_id,
            "aquatone_screenshot_result",
            EVIDENCE_QUALITY_HIGH if screenshots else EVIDENCE_QUALITY_MEDIUM,
            f"Aquatone completed with {len(screenshots)} screenshot artifact(s).",
            {
                "urls": urls,
                "command": list(result.command),
                "returncode": result.returncode,
                "screenshots": screenshots,
                "html_report_path": html_report.as_posix() if html_report.is_file() else None,
                "screenshot_hashes": [item["sha256"] for item in screenshots],
                "stderr": result.stderr,
            },
            "aquatone",
        )
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], result.to_dict() | {"screenshots": screenshots})


class ShodanPassiveIntelTechnique(BaseTechnique):
    """Technique 7: Shodan passive host/search intelligence."""

    technique_id = "osint.shodan_passive_intel"
    module_id = M01_MODULE_ID
    display_name = "Shodan passive intelligence"
    description = "Query Shodan API for passive host or search intelligence."
    tool_name = "Shodan API"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["query", "target_type"]
    optional_inputs = ["api_profile", "result_limit", "include_banners"]
    expected_evidence = ["passive_ports", "banners", "host_metadata", "normalized_json", "source_urls"]
    input_schema = {"query": {"type": "string"}, "target_type": {"enum": ["ip", "domain", "query"]}}
    ai_fillable_inputs = ["query", "result_limit", "include_banners"]
    panel_fields = [{"name": "query", "label": "Query", "type": "text"}]
    success_markers = ["passive_ports", "host_metadata"]
    failure_markers = ["missing_shodan_api_key", "shodan_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"passive_ports": "list", "banners": "list", "host_metadata": "dict"}
    version_lock_id = "m01_osint/shodan-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "query")
        target_type = _choice(context.parameters, "target_type", "query", {"ip", "domain", "query"})
        limit = _optional_int(context.parameters, "result_limit", 10, 1, 100)
        include_banners = _optional_bool(context.parameters, "include_banners", False)
        api_key = _api_key(context.parameters, ("SHODAN_API_KEY",))
        if target_type == "ip":
            url = f"https://api.shodan.io/shodan/host/{query}"
            payload = _http_get_json(url, params={"key": api_key})
            normalized = _normalize_shodan_host(payload["payload"], include_banners)
        else:
            payload = _http_get_json("https://api.shodan.io/shodan/host/search", params={"key": api_key, "query": query, "limit": limit})
            normalized = _normalize_shodan_search(payload["payload"], include_banners)
        evidence = _execution_evidence(context, self.technique_id, "shodan_passive_json", EVIDENCE_QUALITY_HIGH, "Shodan passive intelligence fetched.", normalized | {"source_urls": [payload["url"]]}, "shodan")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], {"api_status_code": payload["status_code"], **normalized})


class CensysPassiveIntelTechnique(BaseTechnique):
    """Technique 8: Censys passive host/certificate intelligence."""

    technique_id = "osint.censys_passive_intel"
    module_id = M01_MODULE_ID
    display_name = "Censys passive intelligence"
    description = "Query Censys API for passive services or certificates."
    tool_name = "Censys API"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["query", "target_type"]
    optional_inputs = ["api_profile", "result_limit", "include_certificates"]
    expected_evidence = ["certificates", "passive_services", "host_metadata", "normalized_json"]
    input_schema = {"query": {"type": "string"}, "target_type": {"enum": ["ip", "domain", "certificate", "query"]}}
    ai_fillable_inputs = ["query", "result_limit", "include_certificates"]
    panel_fields = [{"name": "query", "label": "Query", "type": "text"}]
    success_markers = ["passive_services", "certificates"]
    failure_markers = ["missing_censys_credentials", "censys_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"certificates": "list", "passive_services": "list", "host_metadata": "dict"}
    version_lock_id = "m01_osint/censys-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "query")
        target_type = _choice(context.parameters, "target_type", "query", {"ip", "domain", "certificate", "query"})
        limit = _optional_int(context.parameters, "result_limit", 10, 1, 100)
        api_id = _api_key(context.parameters, ("CENSYS_API_ID",))
        api_secret = _api_key(context.parameters, ("CENSYS_API_SECRET",), parameter_name="api_secret")
        endpoint = "https://search.censys.io/api/v2/hosts/search"
        params = {"q": query, "per_page": limit}
        if target_type == "certificate":
            endpoint = "https://search.censys.io/api/v2/certificates/search"
        payload = requests.get(endpoint, params=params, auth=(api_id, api_secret), timeout=20)
        try:
            body = payload.json()
        except ValueError as error:
            raise ContractError("Censys API response was not valid JSON.") from error
        if not isinstance(body, dict):
            raise ContractError("Censys API response must be a JSON object.")
        normalized = _normalize_censys(body, target_type)
        evidence = _execution_evidence(context, self.technique_id, "censys_passive_json", EVIDENCE_QUALITY_HIGH, "Censys passive intelligence fetched.", normalized | {"source_urls": [payload.url]}, "censys")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], {"api_status_code": payload.status_code, **normalized})


class AlienvaultOtxPassiveIntelTechnique(BaseTechnique):
    """Technique 9: AlienVault OTX passive indicator intelligence."""

    technique_id = "osint.alienvault_otx_passive_intel"
    module_id = M01_MODULE_ID
    display_name = "AlienVault OTX passive intelligence"
    description = "Query AlienVault OTX for passive indicator context."
    tool_name = "AlienVault OTX API"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["indicator", "indicator_type"]
    optional_inputs = ["api_profile", "include_pulses", "include_related"]
    expected_evidence = ["iocs", "related_indicators", "pulses", "normalized_json"]
    input_schema = {"indicator": {"type": "string"}, "indicator_type": {"enum": ["domain", "ip", "url", "hash", "email"]}}
    ai_fillable_inputs = ["indicator_type", "include_pulses", "include_related"]
    panel_fields = [{"name": "indicator", "label": "Indicator", "type": "text"}]
    success_markers = ["iocs", "pulses"]
    failure_markers = ["missing_otx_api_key", "otx_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"iocs": "list", "related_indicators": "list", "pulses": "list"}
    version_lock_id = "m01_osint/alienvault-otx-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        indicator = _require_string(context.parameters, "indicator")
        indicator_type = _choice(context.parameters, "indicator_type", "domain", {"domain", "ip", "url", "hash", "email"})
        api_key = _api_key(context.parameters, ("OTX_API_KEY", "ALIENVAULT_OTX_API_KEY"))
        otx_type = {"domain": "domain", "ip": "IPv4", "url": "url", "hash": "file", "email": "email"}[indicator_type]
        url = f"https://otx.alienvault.com/api/v1/indicators/{otx_type}/{indicator}/general"
        payload = _http_get_json(url, headers={"X-OTX-API-KEY": api_key})
        normalized = _normalize_otx(payload["payload"])
        evidence = _execution_evidence(context, self.technique_id, "otx_passive_json", EVIDENCE_QUALITY_HIGH, "AlienVault OTX passive intelligence fetched.", normalized | {"source_urls": [payload["url"]]}, "alienvault-otx")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], {"api_status_code": payload["status_code"], **normalized})


class SecuritytrailsPassiveIntelTechnique(BaseTechnique):
    """Technique 10: SecurityTrails passive DNS/domain intelligence."""

    technique_id = "osint.securitytrails_passive_intel"
    module_id = M01_MODULE_ID
    display_name = "SecurityTrails passive intelligence"
    description = "Query SecurityTrails for passive DNS, subdomain, and WHOIS context."
    tool_name = "SecurityTrails API"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["domain"]
    optional_inputs = ["api_profile", "include_dns_history", "include_subdomains", "include_whois"]
    expected_evidence = ["dns_history", "subdomains", "whois_records", "normalized_json"]
    input_schema = {"domain": {"type": "string"}, "include_dns_history": {"type": "boolean"}}
    ai_fillable_inputs = ["include_dns_history", "include_subdomains", "include_whois"]
    panel_fields = [{"name": "domain", "label": "Domain", "type": "text"}]
    success_markers = ["dns_history", "subdomains", "whois_records"]
    failure_markers = ["missing_securitytrails_api_key", "securitytrails_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"dns_history": "list", "subdomains": "list", "whois_records": "dict"}
    version_lock_id = "m01_osint/securitytrails-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        domain = _domain_arg(context.parameters)
        api_key = _api_key(context.parameters, ("SECURITYTRAILS_API_KEY",))
        headers = {"APIKEY": api_key}
        include_subdomains = _optional_bool(context.parameters, "include_subdomains", True)
        include_dns_history = _optional_bool(context.parameters, "include_dns_history", True)
        include_whois = _optional_bool(context.parameters, "include_whois", True)
        base = "https://api.securitytrails.com/v1"
        source_urls: list[str] = []
        subdomains: list[str] = []
        dns_history: list[dict[str, Any]] = []
        whois_records: dict[str, Any] = {}
        if include_subdomains:
            payload = _http_get_json(f"{base}/domain/{domain}/subdomains", headers=headers)
            source_urls.append(str(payload["url"]))
            subdomains = _normalize_securitytrails_subdomains(payload["payload"], domain)
        if include_dns_history:
            payload = _http_get_json(f"{base}/history/dns/a/{domain}", headers=headers)
            source_urls.append(str(payload["url"]))
            dns_history = _normalize_securitytrails_dns_history(payload["payload"])
        if include_whois:
            payload = _http_get_json(f"{base}/history/{domain}/whois", headers=headers)
            source_urls.append(str(payload["url"]))
            whois_records = payload["payload"]
        normalized = {
            "domain": domain,
            "subdomains": subdomains,
            "dns_history": dns_history,
            "whois_records": whois_records,
            "attack_surface_updates": _domain_graph_updates(domain, subdomains),
            "source_urls": source_urls,
        }
        evidence = _execution_evidence(context, self.technique_id, "securitytrails_passive_json", EVIDENCE_QUALITY_HIGH, "SecurityTrails passive intelligence fetched.", normalized, "securitytrails")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class HibpEmailLeakLookupTechnique(BaseTechnique):
    """Technique 11: Have I Been Pwned breach and paste lookup."""

    technique_id = "osint.hibp_email_leak_lookup"
    module_id = M01_MODULE_ID
    display_name = "HIBP email leak lookup"
    description = "Query Have I Been Pwned for breach and paste exposure for an email address."
    tool_name = "Have I Been Pwned API"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["email"]
    optional_inputs = ["api_profile", "include_pastes", "include_breaches", "redact_sensitive"]
    expected_evidence = ["breach_names", "paste_findings", "exposure_summary", "normalized_json"]
    input_schema = {"email": {"type": "string"}, "include_pastes": {"type": "boolean"}, "include_breaches": {"type": "boolean"}}
    ai_fillable_inputs = ["include_pastes", "include_breaches", "redact_sensitive"]
    panel_fields = [{"name": "email", "label": "Email", "type": "email"}]
    success_markers = ["breach_names", "exposure_summary"]
    failure_markers = ["missing_hibp_api_key", "hibp_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"breach_names": "list", "paste_findings": "list", "exposure_summary": "dict"}
    version_lock_id = "m01_osint/hibp-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        email = _email_arg(_require_string(context.parameters, "email"))
        api_key = _api_key(context.parameters, ("HIBP_API_KEY",))
        include_breaches = _optional_bool(context.parameters, "include_breaches", True)
        include_pastes = _optional_bool(context.parameters, "include_pastes", False)
        redact = _optional_bool(context.parameters, "redact_sensitive", True)
        headers = {"hibp-api-key": api_key, "user-agent": "ojo-de-dios-m01"}
        breach_names: list[str] = []
        paste_findings: list[dict[str, Any]] = []
        source_urls: list[str] = []
        if include_breaches:
            response = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", params={"truncateResponse": "false"}, headers=headers, timeout=20)
            source_urls.append(response.url)
            breach_names = _normalize_hibp_breaches(_json_or_empty_list(response))
        if include_pastes:
            response = requests.get(f"https://haveibeenpwned.com/api/v3/pasteaccount/{email}", headers=headers, timeout=20)
            source_urls.append(response.url)
            paste_findings = _normalize_hibp_pastes(_json_or_empty_list(response))
        normalized = {
            "email": _redact_email(email) if redact else email,
            "breach_names": breach_names,
            "paste_findings": paste_findings,
            "exposure_summary": {"breach_count": len(breach_names), "paste_count": len(paste_findings), "redacted": redact, "queried_email": _redact_email(email) if redact else email},
            "source_urls": source_urls,
        }
        evidence = _execution_evidence(context, self.technique_id, "hibp_passive_json", EVIDENCE_QUALITY_HIGH, "HIBP passive exposure lookup completed.", normalized, "hibp")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class DehashedLookupTechnique(BaseTechnique):
    """Technique 12: Dehashed passive exposure lookup."""

    technique_id = "osint.dehashed_lookup"
    module_id = M01_MODULE_ID
    display_name = "Dehashed lookup"
    description = "Query Dehashed for passive exposure records and redact sensitive values by default."
    tool_name = "Dehashed API"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["query", "query_type"]
    optional_inputs = ["api_profile", "result_limit", "redact_sensitive"]
    expected_evidence = ["exposure_records", "redacted_summary", "normalized_json"]
    input_schema = {"query": {"type": "string"}, "query_type": {"enum": ["email", "domain", "username", "phone", "hash"]}}
    ai_fillable_inputs = ["query_type", "result_limit", "redact_sensitive"]
    panel_fields = [{"name": "query", "label": "Query", "type": "text"}]
    success_markers = ["exposure_records"]
    failure_markers = ["missing_dehashed_credentials", "dehashed_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"exposure_records": "list", "redacted_summary": "dict"}
    version_lock_id = "m01_osint/dehashed-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "query")
        query_type = _choice(context.parameters, "query_type", "email", {"email", "domain", "username", "phone", "hash"})
        limit = _optional_int(context.parameters, "result_limit", 25, 1, 1000)
        redact = _optional_bool(context.parameters, "redact_sensitive", True)
        username = _api_key(context.parameters, ("DEHASHED_USERNAME", "DEHASHED_EMAIL"))
        api_key = _api_key(context.parameters, ("DEHASHED_API_KEY",), parameter_name="api_secret")
        response = requests.get("https://api.dehashed.com/search", params={"query": f"{query_type}:{query}", "size": limit}, auth=(username, api_key), timeout=20)
        payload = _json_object_response(response, "Dehashed")
        records = _normalize_dehashed(payload, redact)
        normalized = {"query_type": query_type, "exposure_records": records, "redacted_summary": {"record_count": len(records), "redacted": redact}, "source_urls": [response.url]}
        evidence = _execution_evidence(context, self.technique_id, "dehashed_passive_json", EVIDENCE_QUALITY_HIGH, "Dehashed passive exposure lookup completed.", normalized, "dehashed")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class IntelxLookupTechnique(BaseTechnique):
    """Technique 13: Intelligence X passive lookup."""

    technique_id = "osint.intelx_lookup"
    module_id = M01_MODULE_ID
    display_name = "IntelX lookup"
    description = "Query Intelligence X for passive OSINT records."
    tool_name = "IntelX API"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["query", "query_type"]
    optional_inputs = ["api_profile", "result_limit", "source_profile"]
    expected_evidence = ["intel_records", "source_references", "normalized_json"]
    input_schema = {"query": {"type": "string"}, "query_type": {"enum": ["email", "domain", "ip", "phone", "hash", "keyword"]}}
    ai_fillable_inputs = ["query_type", "result_limit", "source_profile"]
    panel_fields = [{"name": "query", "label": "Query", "type": "text"}]
    success_markers = ["intel_records"]
    failure_markers = ["missing_intelx_api_key", "intelx_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"intel_records": "list", "source_references": "list"}
    version_lock_id = "m01_osint/intelx-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "query")
        query_type = _choice(context.parameters, "query_type", "keyword", {"email", "domain", "ip", "phone", "hash", "keyword"})
        limit = _optional_int(context.parameters, "result_limit", 20, 1, 100)
        api_key = _api_key(context.parameters, ("INTELX_API_KEY",))
        response = requests.post("https://2.intelx.io/intelligent/search", headers={"x-key": api_key}, json={"term": query, "maxresults": limit, "media": 0, "target": 0}, timeout=20)
        payload = _json_object_response(response, "IntelX")
        normalized = _normalize_intelx(payload, query_type, response.url)
        evidence = _execution_evidence(context, self.technique_id, "intelx_passive_json", EVIDENCE_QUALITY_HIGH, "IntelX passive lookup submitted.", normalized, "intelx")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class SpiderfootAutomationTechnique(BaseTechnique):
    """Technique 14: SpiderFoot CLI/API automation."""

    technique_id = "osint.spiderfoot_automation"
    module_id = M01_MODULE_ID
    display_name = "SpiderFoot automation"
    description = "Run a local SpiderFoot CLI scan profile or query a configured SpiderFoot HX API endpoint."
    tool_name = "SpiderFoot / SpiderFoot HX"
    recommended_version = "v4.0 latest-release-lock"
    runtime = "python_lib_or_api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["target", "target_type"]
    optional_inputs = ["scan_profile", "modules_profile", "api_profile", "result_limit"]
    expected_evidence = ["osint_graph", "discovered_entities", "relationship_edges", "normalized_json", "report_path"]
    input_schema = {"target": {"type": "string"}, "target_type": {"enum": ["domain", "ip", "email", "username", "company"]}}
    ai_fillable_inputs = ["target_type", "scan_profile", "modules_profile", "result_limit"]
    panel_fields = [{"name": "target", "label": "Target", "type": "text"}]
    success_markers = ["discovered_entities", "relationship_edges"]
    failure_markers = ["missing_spiderfoot", "spiderfoot_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"osint_graph": "dict", "discovered_entities": "list", "relationship_edges": "list"}
    version_lock_id = "m01_osint/spiderfoot"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        target = _require_string(context.parameters, "target")
        target_type = _choice(context.parameters, "target_type", "domain", {"domain", "ip", "email", "username", "company"})
        api_url = str(context.parameters.get("api_url") or os.environ.get("SPIDERFOOT_API_URL", "")).strip()
        if api_url:
            api_key = str(context.parameters.get("api_key") or os.environ.get("SPIDERFOOT_API_KEY", "")).strip()
            payload = _http_get_json(api_url.rstrip("/") + "/scan/new", headers={"Authorization": f"Bearer {api_key}"} if api_key else None, params={"target": target, "type": target_type})
            normalized = _normalize_spiderfoot_api(payload["payload"], payload["url"])
        else:
            spiderfoot_path = _tool_path("sfcli") or _tool_path("spiderfoot")
            if spiderfoot_path is None:
                return _missing_tool_result(self.technique_id, ["sfcli", "spiderfoot"])
            result = _run_command([spiderfoot_path, "-s", target, "-t", target_type, "-o", "json"], _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
            normalized = _normalize_spiderfoot_cli(result.stdout, list(result.command))
        evidence = _execution_evidence(context, self.technique_id, "spiderfoot_osint_json", EVIDENCE_QUALITY_HIGH, "SpiderFoot automation completed.", normalized, "spiderfoot")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class TheharvesterEmailsTechnique(BaseTechnique):
    """Technique 15: theHarvester email and host collection."""

    technique_id = "osint.theharvester_emails"
    module_id = M01_MODULE_ID
    display_name = "theHarvester emails"
    description = "Run theHarvester for passive emails and hosts for a domain."
    tool_name = "theHarvester"
    recommended_version = "4.5.0"
    runtime = "python_lib"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["domain"]
    optional_inputs = ["source_profile", "result_limit", "include_hosts", "include_emails"]
    expected_evidence = ["emails", "hosts", "subdomains", "source_references", "normalized_json"]
    input_schema = {"domain": {"type": "string"}, "result_limit": {"type": "integer"}}
    ai_fillable_inputs = ["source_profile", "result_limit", "include_hosts", "include_emails"]
    panel_fields = [{"name": "domain", "label": "Domain", "type": "text"}]
    success_markers = ["emails", "hosts"]
    failure_markers = ["missing_theharvester", "theharvester_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"emails": "list", "hosts": "list", "subdomains": "list"}
    version_lock_id = "m01_osint/theharvester"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        domain = _domain_arg(context.parameters)
        limit = _optional_int(context.parameters, "result_limit", 100, 1, 1000)
        harvester_path = _tool_path("theHarvester")
        if harvester_path is None:
            return _missing_tool_result(self.technique_id, ["theHarvester"])
        source_profile = _choice(context.parameters, "source_profile", "default", {"default", "search_engines", "apis", "custom"})
        source = "bing" if source_profile in {"default", "search_engines"} else "all"
        result = _run_command([harvester_path, "-d", domain, "-b", source, "-l", str(limit), "-f", "-"], _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
        normalized = _normalize_theharvester(result.stdout, domain, list(result.command))
        evidence = _execution_evidence(context, self.technique_id, "theharvester_json_result", EVIDENCE_QUALITY_HIGH, "theHarvester collection completed.", normalized, "theHarvester")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class HoleheEmailCheckTechnique(BaseTechnique):
    """Technique 16: Holehe public account presence check."""

    technique_id = "osint.holehe_email_check"
    module_id = M01_MODULE_ID
    display_name = "Holehe email check"
    description = "Run Holehe against one email to observe public account presence signals."
    tool_name = "Holehe"
    recommended_version = "1.64 latest-release-lock"
    runtime = "python_lib"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["email"]
    optional_inputs = ["site_profile", "result_limit", "timeout_seconds"]
    expected_evidence = ["account_presence_findings", "site_matches", "normalized_json"]
    input_schema = {"email": {"type": "string"}, "timeout_seconds": {"type": "integer"}}
    ai_fillable_inputs = ["site_profile", "result_limit", "timeout_seconds"]
    panel_fields = [{"name": "email", "label": "Email", "type": "email"}]
    success_markers = ["site_matches"]
    failure_markers = ["missing_holehe", "holehe_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"account_presence_findings": "list", "site_matches": "list"}
    version_lock_id = "m01_osint/holehe"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        email = _email_arg(_require_string(context.parameters, "email"))
        holehe_path = _tool_path("holehe")
        if holehe_path is None:
            return _missing_tool_result(self.technique_id, ["holehe"])
        result = _run_command([holehe_path, "--no-color", email], _optional_int(context.parameters, "timeout_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
        normalized = _normalize_holehe(result.stdout, email)
        evidence = _execution_evidence(context, self.technique_id, "holehe_text_result", EVIDENCE_QUALITY_HIGH, "Holehe email check completed.", normalized, "holehe")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class SherlockUsernameTechnique(BaseTechnique):
    """Technique 17: Sherlock username profile lookup."""

    technique_id = "osint.sherlock_username"
    module_id = M01_MODULE_ID
    display_name = "Sherlock username"
    description = "Run Sherlock for public username profiles."
    tool_name = "Sherlock"
    recommended_version = "0.15 latest-release-lock"
    runtime = "python_lib"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["username"]
    optional_inputs = ["site_profile", "include_nsfw", "timeout_seconds", "output_format"]
    expected_evidence = ["social_profiles", "profile_urls", "normalized_json", "report_path"]
    input_schema = {"username": {"type": "string"}}
    ai_fillable_inputs = ["site_profile", "timeout_seconds", "output_format"]
    panel_fields = [{"name": "username", "label": "Username", "type": "text"}]
    success_markers = ["social_profiles", "profile_urls"]
    failure_markers = ["missing_sherlock", "sherlock_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"social_profiles": "list", "profile_urls": "list"}
    version_lock_id = "m01_osint/sherlock"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        username = _safe_identifier(_require_string(context.parameters, "username"), "username")
        sherlock_path = _tool_path("sherlock")
        if sherlock_path is None:
            return _missing_tool_result(self.technique_id, ["sherlock"])
        result = _run_command([sherlock_path, username, "--print-found", "--timeout", str(_optional_int(context.parameters, "timeout_seconds", 60, 5, 600))], _optional_int(context.parameters, "timeout_seconds", 60, 5, 600))
        normalized = _normalize_profile_lines(result.stdout, username)
        evidence = _execution_evidence(context, self.technique_id, "sherlock_profile_result", EVIDENCE_QUALITY_HIGH, "Sherlock username lookup completed.", normalized, "sherlock")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class MaigretProfilesTechnique(SherlockUsernameTechnique):
    """Technique 18: Maigret username profile lookup."""

    technique_id = "osint.maigret_profiles"
    display_name = "Maigret profiles"
    description = "Run Maigret for public username profiles."
    tool_name = "Maigret"
    recommended_version = "0.4 latest-release-lock"
    optional_inputs = ["profile_depth", "report_format", "site_profile", "timeout_seconds"]
    ai_fillable_inputs = ["profile_depth", "report_format", "site_profile"]
    failure_markers = ["missing_maigret", "maigret_nonzero_exit"]
    version_lock_id = "m01_osint/maigret"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        username = _safe_identifier(_require_string(context.parameters, "username"), "username")
        maigret_path = _tool_path("maigret")
        if maigret_path is None:
            return _missing_tool_result(self.technique_id, ["maigret"])
        result = _run_command([maigret_path, username, "--no-color"], _optional_int(context.parameters, "timeout_seconds", 120, 5, 1200))
        normalized = _normalize_profile_lines(result.stdout, username)
        evidence = _execution_evidence(context, self.technique_id, "maigret_profile_result", EVIDENCE_QUALITY_HIGH, "Maigret profile lookup completed.", normalized, "maigret")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class GhuntGoogleInfoTechnique(BaseTechnique):
    """Technique 19: GHunt public Google identifier lookup."""

    technique_id = "osint.ghunt_google_info"
    module_id = M01_MODULE_ID
    display_name = "GHunt Google info"
    description = "Run GHunt using an operator-managed session profile."
    tool_name = "GHunt"
    recommended_version = "2.0 latest-release-lock"
    runtime = "python_lib"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["google_identifier", "identifier_type", "session_profile"]
    optional_inputs = ["include_public_profile", "output_format"]
    expected_evidence = ["google_profile_findings", "public_identifiers", "normalized_json", "report_path"]
    input_schema = {"google_identifier": {"type": "string"}, "identifier_type": {"enum": ["email", "gaia_id", "username"]}}
    ai_fillable_inputs = ["identifier_type", "include_public_profile", "output_format"]
    panel_fields = [{"name": "google_identifier", "label": "Google identifier", "type": "text"}]
    success_markers = ["google_profile_findings", "public_identifiers"]
    failure_markers = ["missing_ghunt", "missing_session_profile", "ghunt_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"google_profile_findings": "list", "public_identifiers": "list"}
    version_lock_id = "m01_osint/ghunt"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        identifier = _require_string(context.parameters, "google_identifier")
        identifier_type = _choice(context.parameters, "identifier_type", "email", {"email", "gaia_id", "username"})
        _require_string(context.parameters, "session_profile")
        ghunt_path = _tool_path("ghunt")
        if ghunt_path is None:
            return _missing_tool_result(self.technique_id, ["ghunt"])
        mode = "email" if identifier_type == "email" else "gaia" if identifier_type == "gaia_id" else "drive"
        result = _run_command([ghunt_path, mode, identifier], _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1200))
        normalized = _normalize_ghunt(result.stdout, identifier)
        evidence = _execution_evidence(context, self.technique_id, "ghunt_google_profile_result", EVIDENCE_QUALITY_HIGH, "GHunt lookup completed.", normalized, "ghunt")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class FocaMetadataExtractTechnique(BaseTechnique):
    """Technique 20: FOCA metadata extraction from files."""

    technique_id = "osint.foca_metadata_extract"
    module_id = M01_MODULE_ID
    display_name = "FOCA metadata extract"
    description = "Run FOCA CLI when available and normalize metadata output."
    tool_name = "FOCA"
    recommended_version = "latest-release-lock"
    runtime = "windows"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["input_files"]
    optional_inputs = ["input_urls", "metadata_profile", "output_format", "redact_sensitive"]
    expected_evidence = ["metadata_findings", "authors", "software_versions", "paths", "normalized_json", "report_path"]
    input_schema = {"input_files": {"type": "array"}, "redact_sensitive": {"type": "boolean"}}
    ai_fillable_inputs = ["metadata_profile", "output_format", "redact_sensitive"]
    panel_fields = [{"name": "input_files", "label": "Input files", "type": "textarea"}]
    success_markers = ["metadata_findings", "authors"]
    failure_markers = ["missing_foca", "foca_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"metadata_findings": "list", "authors": "list", "software_versions": "list"}
    version_lock_id = "m01_osint/foca"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        files = _existing_files(context.parameters, "input_files")
        foca_path = _tool_path("foca")
        if foca_path is None:
            return _missing_tool_result(self.technique_id, ["foca"])
        result = _run_command([foca_path, "--json", *[path.as_posix() for path in files]], _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1200))
        normalized = _normalize_metadata_json_or_text(result.stdout, _optional_bool(context.parameters, "redact_sensitive", True))
        evidence = _execution_evidence(context, self.technique_id, "foca_metadata_result", EVIDENCE_QUALITY_HIGH, "FOCA metadata extraction completed.", normalized, "foca")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class ExiftoolMetadataExtractTechnique(BaseTechnique):
    """Technique 21: exiftool metadata extraction from local files."""

    technique_id = "osint.exiftool_metadata_extract"
    module_id = M01_MODULE_ID
    display_name = "exiftool metadata extract"
    description = "Run exiftool against local files and normalize metadata."
    tool_name = "exiftool"
    recommended_version = "12.80 latest-release-lock"
    runtime = "windows"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["input_files"]
    optional_inputs = ["recursive", "metadata_profile", "output_format", "redact_sensitive"]
    expected_evidence = ["metadata_findings", "gps_metadata", "device_metadata", "software_metadata", "normalized_json"]
    input_schema = {"input_files": {"type": "array"}, "recursive": {"type": "boolean"}}
    ai_fillable_inputs = ["metadata_profile", "output_format", "redact_sensitive"]
    panel_fields = [{"name": "input_files", "label": "Input files", "type": "textarea"}]
    success_markers = ["metadata_findings"]
    failure_markers = ["missing_exiftool", "exiftool_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"metadata_findings": "list", "gps_metadata": "list", "device_metadata": "list"}
    version_lock_id = "m01_osint/exiftool"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        files = _existing_files(context.parameters, "input_files")
        exiftool_path = _tool_path("exiftool")
        if exiftool_path is None:
            return _missing_tool_result(self.technique_id, ["exiftool"])
        command = [exiftool_path, "-json"]
        if _optional_bool(context.parameters, "recursive", False):
            command.append("-r")
        command.extend(path.as_posix() for path in files)
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1200))
        normalized = _normalize_exiftool(result.stdout, _optional_bool(context.parameters, "redact_sensitive", True))
        evidence = _execution_evidence(context, self.technique_id, "exiftool_metadata_result", EVIDENCE_QUALITY_HIGH, "exiftool metadata extraction completed.", normalized, "exiftool")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class GoogleDorksAutoTechnique(BaseTechnique):
    """Technique 22: search-provider dork connector."""

    technique_id = "osint.google_dorks_auto"
    module_id = M01_MODULE_ID
    display_name = "Google dorks auto"
    description = "Use a configured search API connector for passive dork queries."
    tool_name = "custom_python_search_connector"
    recommended_version = "internal"
    runtime = "python_lib"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["target", "dork_profile"]
    optional_inputs = ["search_provider_profile", "result_limit", "proxy_profile", "redact_sensitive"]
    expected_evidence = ["search_results", "exposed_documents", "exposed_paths", "source_urls", "normalized_json"]
    input_schema = {"target": {"type": "string"}, "dork_profile": {"enum": ["documents", "backups", "panels", "configs", "custom"]}}
    ai_fillable_inputs = ["dork_profile", "result_limit", "redact_sensitive"]
    panel_fields = [{"name": "target", "label": "Target", "type": "text"}]
    success_markers = ["search_results"]
    failure_markers = ["missing_search_api_key", "search_api_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"search_results": "list", "exposed_documents": "list", "exposed_paths": "list"}
    version_lock_id = "m01_osint/search-connector"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        target = _require_string(context.parameters, "target")
        profile = _choice(context.parameters, "dork_profile", "documents", {"documents", "backups", "panels", "configs", "custom"})
        limit = _optional_int(context.parameters, "result_limit", 10, 1, 100)
        api_key = _api_key(context.parameters, ("GOOGLE_CUSTOM_SEARCH_API_KEY", "SERPAPI_API_KEY"))
        cx = str(context.parameters.get("search_engine_id") or os.environ.get("GOOGLE_CUSTOM_SEARCH_CX", "")).strip()
        query = _dork_query(target, profile)
        if cx:
            payload = _http_get_json("https://www.googleapis.com/customsearch/v1", params={"key": api_key, "cx": cx, "q": query, "num": min(limit, 10)})
        else:
            payload = _http_get_json("https://serpapi.com/search.json", params={"api_key": api_key, "engine": "google", "q": query, "num": limit})
        normalized = _normalize_search_results(payload["payload"], payload["url"])
        evidence = _execution_evidence(context, self.technique_id, "search_dorks_json", EVIDENCE_QUALITY_HIGH, "Search dork connector completed.", normalized, "search-api")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class IpGeolocationAsnBgpTechnique(BaseTechnique):
    """Technique 23: passive IP/ASN/BGP enrichment."""

    technique_id = "osint.ip_geolocation_asn_bgp"
    module_id = M01_MODULE_ID
    display_name = "IP geolocation ASN BGP"
    description = "Query RIPE Stat for passive IP, ASN, and prefix information."
    tool_name = "bgp.he.net + custom scripts"
    recommended_version = "internal"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["ip_or_asn", "lookup_type"]
    optional_inputs = ["include_prefixes", "include_peers", "output_format"]
    expected_evidence = ["asn_records", "bgp_prefixes", "geolocation", "normalized_json"]
    input_schema = {"ip_or_asn": {"type": "string"}, "lookup_type": {"enum": ["ip", "asn", "prefix"]}}
    ai_fillable_inputs = ["lookup_type", "include_prefixes", "include_peers"]
    panel_fields = [{"name": "ip_or_asn", "label": "IP/ASN/Prefix", "type": "text"}]
    success_markers = ["asn_records", "bgp_prefixes"]
    failure_markers = ["ripe_stat_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"asn_records": "list", "bgp_prefixes": "list", "geolocation": "dict"}
    version_lock_id = "m01_osint/ripe-stat-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        resource = _require_string(context.parameters, "ip_or_asn").upper().replace("AS", "")
        lookup_type = _choice(context.parameters, "lookup_type", "ip", {"ip", "asn", "prefix"})
        payload = _http_get_json("https://stat.ripe.net/data/prefix-overview/data.json", params={"resource": resource})
        normalized = _normalize_ripe_stat(payload["payload"], lookup_type, payload["url"])
        evidence = _execution_evidence(context, self.technique_id, "ripe_stat_json", EVIDENCE_QUALITY_HIGH, "RIPE Stat passive enrichment completed.", normalized, "ripe-stat")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class WhoisHistoryTechnique(BaseTechnique):
    """Technique 24: WHOIS/RDAP current and optional history lookup."""

    technique_id = "osint.whois_history"
    module_id = M01_MODULE_ID
    display_name = "WHOIS history"
    description = "Fetch current RDAP and optional WhoisXMLAPI history when configured."
    tool_name = "ViewDNS.info / WhoisXMLAPI"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["domain"]
    optional_inputs = ["provider_profile", "include_history", "output_format"]
    expected_evidence = ["whois_records", "historical_ownership", "registrar_history", "normalized_json"]
    input_schema = {"domain": {"type": "string"}, "include_history": {"type": "boolean"}}
    ai_fillable_inputs = ["provider_profile", "include_history"]
    panel_fields = [{"name": "domain", "label": "Domain", "type": "text"}]
    success_markers = ["whois_records"]
    failure_markers = ["whois_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"whois_records": "dict", "historical_ownership": "list", "registrar_history": "list"}
    version_lock_id = "m01_osint/whois-history"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        domain = _domain_arg(context.parameters)
        include_history = _optional_bool(context.parameters, "include_history", False)
        current = _http_get_json(f"https://rdap.org/domain/{domain}", headers={"Accept": "application/rdap+json, application/json"})
        historical_ownership: list[dict[str, Any]] = []
        source_urls = [current["url"]]
        if include_history and (os.environ.get("WHOISXMLAPI_KEY") or context.parameters.get("api_key")):
            key = _api_key(context.parameters, ("WHOISXMLAPI_KEY",))
            history = _http_get_json("https://www.whoisxmlapi.com/whoisserver/WhoisService", params={"apiKey": key, "domainName": domain, "outputFormat": "JSON"})
            source_urls.append(str(history["url"]))
            historical_ownership = _normalize_whois_history(history["payload"])
        normalized = _normalize_rdap_whois(current["payload"], historical_ownership, source_urls)
        evidence = _execution_evidence(context, self.technique_id, "whois_history_json", EVIDENCE_QUALITY_HIGH, "WHOIS/RDAP lookup completed.", normalized, "rdap-whois")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class ReverseDnsTechnique(BaseTechnique):
    """Technique 25: passive reverse DNS lookup."""

    technique_id = "osint.reverse_dns"
    module_id = M01_MODULE_ID
    display_name = "Reverse DNS"
    description = "Resolve PTR records for a single IP or a bounded prefix sample."
    tool_name = "ViewDNS.info / custom scripts"
    recommended_version = "latest"
    runtime = "api"
    worker = "windows"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["ip_or_range"]
    optional_inputs = ["provider_profile", "result_limit", "output_format"]
    expected_evidence = ["reverse_dns_records", "domains", "normalized_json"]
    input_schema = {"ip_or_range": {"type": "string"}, "result_limit": {"type": "integer"}}
    ai_fillable_inputs = ["result_limit"]
    panel_fields = [{"name": "ip_or_range", "label": "IP/range", "type": "text"}]
    success_markers = ["reverse_dns_records", "domains"]
    failure_markers = ["reverse_dns_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"reverse_dns_records": "list", "domains": "list"}
    version_lock_id = "m01_osint/reverse-dns"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        value = _require_string(context.parameters, "ip_or_range")
        limit = _optional_int(context.parameters, "result_limit", 16, 1, 256)
        records = _reverse_dns_records(value, limit)
        normalized = {"ip_or_range": value, "reverse_dns_records": records, "domains": sorted({name for record in records for name in record.get("domains", [])})}
        evidence = _execution_evidence(context, self.technique_id, "reverse_dns_json", EVIDENCE_QUALITY_HIGH if records else EVIDENCE_QUALITY_MEDIUM, "Reverse DNS lookup completed.", normalized, "socket-ptr")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class LinkedinSocialOsintTechnique(BaseTechnique):
    """Technique 26: passive LinkedIn-oriented search connector."""

    technique_id = "osint.linkedin_social_osint"
    module_id = M01_MODULE_ID
    display_name = "LinkedIn social OSINT"
    description = "Use a configured search API to find public LinkedIn profile and company references."
    tool_name = "custom_playwright_connector"
    recommended_version = "internal"
    runtime = "browser_automation"
    worker = "BrowserAutomationWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["query", "query_type"]
    optional_inputs = ["session_profile", "source_profile", "result_limit", "redact_sensitive"]
    expected_evidence = ["social_profiles", "company_profiles", "relationship_hints", "normalized_json"]
    input_schema = {"query": {"type": "string"}, "query_type": {"enum": ["person", "company", "domain", "email"]}}
    ai_fillable_inputs = ["query_type", "result_limit", "redact_sensitive"]
    panel_fields = [{"name": "query", "label": "Query", "type": "text"}]
    success_markers = ["social_profiles", "company_profiles"]
    failure_markers = ["missing_search_api_key", "linkedin_search_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"social_profiles": "list", "company_profiles": "list", "relationship_hints": "list"}
    version_lock_id = "m01_osint/linkedin-search-connector"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "query")
        query_type = _choice(context.parameters, "query_type", "person", {"person", "company", "domain", "email"})
        limit = _optional_int(context.parameters, "result_limit", 10, 1, 100)
        api_key = _api_key(context.parameters, ("GOOGLE_CUSTOM_SEARCH_API_KEY", "SERPAPI_API_KEY"))
        cx = str(context.parameters.get("search_engine_id") or os.environ.get("GOOGLE_CUSTOM_SEARCH_CX", "")).strip()
        search_query = f'site:linkedin.com/in OR site:linkedin.com/company "{query}"'
        payload = _search_provider_payload(api_key, search_query, limit, cx)
        normalized = _normalize_social_search(payload["payload"], payload["url"], "linkedin", query, query_type, _optional_bool(context.parameters, "redact_sensitive", True))
        evidence = _execution_evidence(context, self.technique_id, "linkedin_social_search_json", EVIDENCE_QUALITY_HIGH, "LinkedIn public search completed.", normalized, "search-api")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class TwitterSocialOsintTechnique(BaseTechnique):
    """Technique 27: passive X/Twitter social search."""

    technique_id = "osint.twitter_social_osint"
    module_id = M01_MODULE_ID
    display_name = "Twitter social OSINT"
    description = "Query the X API when configured or a search connector for public X/Twitter mentions."
    tool_name = "custom_playwright_connector"
    recommended_version = "internal"
    runtime = "browser_automation"
    worker = "BrowserAutomationWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["query", "query_type"]
    optional_inputs = ["session_profile", "source_profile", "result_limit", "redact_sensitive"]
    expected_evidence = ["social_profiles", "mentions", "relationship_hints", "normalized_json"]
    input_schema = {"query": {"type": "string"}, "query_type": {"enum": ["person", "company", "domain", "email", "keyword"]}}
    ai_fillable_inputs = ["query_type", "result_limit", "redact_sensitive"]
    panel_fields = [{"name": "query", "label": "Query", "type": "text"}]
    success_markers = ["social_profiles", "mentions"]
    failure_markers = ["missing_search_api_key", "twitter_search_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"social_profiles": "list", "mentions": "list", "relationship_hints": "list"}
    version_lock_id = "m01_osint/twitter-search-connector"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "query")
        query_type = _choice(context.parameters, "query_type", "keyword", {"person", "company", "domain", "email", "keyword"})
        limit = _optional_int(context.parameters, "result_limit", 10, 1, 100)
        bearer = str(context.parameters.get("bearer_token") or os.environ.get("TWITTER_BEARER_TOKEN", "")).strip()
        if bearer:
            payload = _http_get_json("https://api.twitter.com/2/tweets/search/recent", headers={"Authorization": f"Bearer {bearer}"}, params={"query": query, "max_results": max(10, min(limit, 100)), "tweet.fields": "author_id,created_at,entities"})
            normalized = _normalize_twitter_api(payload["payload"], payload["url"], query, _optional_bool(context.parameters, "redact_sensitive", True))
        else:
            api_key = _api_key(context.parameters, ("GOOGLE_CUSTOM_SEARCH_API_KEY", "SERPAPI_API_KEY"))
            cx = str(context.parameters.get("search_engine_id") or os.environ.get("GOOGLE_CUSTOM_SEARCH_CX", "")).strip()
            payload = _search_provider_payload(api_key, f'site:twitter.com OR site:x.com "{query}"', limit, cx)
            normalized = _normalize_social_search(payload["payload"], payload["url"], "twitter", query, query_type, _optional_bool(context.parameters, "redact_sensitive", True))
            normalized["mentions"] = normalized.pop("social_profiles")
            normalized["social_profiles"] = []
        evidence = _execution_evidence(context, self.technique_id, "twitter_social_search_json", EVIDENCE_QUALITY_HIGH, "Twitter/X public search completed.", normalized, "twitter-search")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class GithubSocialOsintTechnique(BaseTechnique):
    """Technique 28: GitHub API passive social/code OSINT."""

    technique_id = "osint.github_social_osint"
    module_id = M01_MODULE_ID
    display_name = "GitHub social OSINT"
    description = "Use GitHub search APIs for users, organizations, repositories, and exposed references."
    tool_name = "GitHub API / custom_playwright_connector"
    recommended_version = "latest"
    runtime = "api_or_browser_automation"
    worker = "APIWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["query", "query_type"]
    optional_inputs = ["api_profile", "result_limit", "include_repositories", "include_users"]
    expected_evidence = ["github_profiles", "repositories", "exposed_references", "normalized_json"]
    input_schema = {"query": {"type": "string"}, "query_type": {"enum": ["username", "organization", "domain", "email", "keyword"]}}
    ai_fillable_inputs = ["query_type", "result_limit", "include_repositories", "include_users"]
    panel_fields = [{"name": "query", "label": "Query", "type": "text"}]
    success_markers = ["github_profiles", "repositories"]
    failure_markers = ["github_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"github_profiles": "list", "repositories": "list", "exposed_references": "list"}
    version_lock_id = "m01_osint/github-api"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "query")
        query_type = _choice(context.parameters, "query_type", "keyword", {"username", "organization", "domain", "email", "keyword"})
        limit = _optional_int(context.parameters, "result_limit", 10, 1, 100)
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        token = str(context.parameters.get("api_key") or os.environ.get("GITHUB_TOKEN", "")).strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        responses = []
        if _optional_bool(context.parameters, "include_users", True):
            responses.append(_http_get_json("https://api.github.com/search/users", headers=headers, params={"q": query, "per_page": min(limit, 100)}))
        if _optional_bool(context.parameters, "include_repositories", True):
            responses.append(_http_get_json("https://api.github.com/search/repositories", headers=headers, params={"q": query, "per_page": min(limit, 100)}))
        normalized = _normalize_github_search([item["payload"] for item in responses], [str(item["url"]) for item in responses], query_type)
        evidence = _execution_evidence(context, self.technique_id, "github_social_json", EVIDENCE_QUALITY_HIGH, "GitHub passive OSINT completed.", normalized, "github-api")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class TrufflehogRepoLeaksTechnique(BaseTechnique):
    """Technique 29: truffleHog passive repository secret scan."""

    technique_id = "osint.trufflehog_repo_leaks"
    module_id = M01_MODULE_ID
    display_name = "truffleHog repo leaks"
    description = "Run truffleHog against an operator-supplied local path or repository URL and redact raw secrets."
    tool_name = "truffleHog"
    recommended_version = "3.69 latest-release-lock"
    runtime = "windows"
    worker = "WindowsWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = []
    optional_inputs = ["repository_url", "local_path", "scan_profile", "redact_secrets", "output_format"]
    expected_evidence = ["secret_findings", "redacted_findings", "raw_output_path", "normalized_json"]
    input_schema = {"repository_url": {"type": "string"}, "local_path": {"type": "string"}}
    ai_fillable_inputs = ["scan_profile", "redact_secrets", "output_format"]
    panel_fields = [{"name": "repository_url", "label": "Repository URL", "type": "url"}]
    success_markers = ["secret_findings", "redacted_findings"]
    failure_markers = ["missing_trufflehog", "trufflehog_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"secret_findings": "list", "redacted_findings": "list"}
    version_lock_id = "m01_osint/trufflehog"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        target = _repo_scan_target(context.parameters)
        tool = _tool_path("trufflehog") or _tool_path("truffleHog")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["trufflehog"])
        command = [tool, "filesystem" if Path(target).exists() else "git", target, "--json"]
        if _choice(context.parameters, "scan_profile", "standard", {"standard", "deep"}) == "deep":
            command.append("--no-update")
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
        normalized = _normalize_secret_scan(result.stdout, "trufflehog", _optional_bool(context.parameters, "redact_secrets", True))
        evidence = _execution_evidence(context, self.technique_id, "trufflehog_json", EVIDENCE_QUALITY_HIGH, "truffleHog repository scan completed.", normalized, "trufflehog")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class GitleaksRepoLeaksTechnique(BaseTechnique):
    """Technique 30: Gitleaks passive repository secret scan."""

    technique_id = "osint.gitleaks_repo_leaks"
    module_id = M01_MODULE_ID
    display_name = "Gitleaks repo leaks"
    description = "Run Gitleaks against an operator-supplied repository or local path and normalize redacted findings."
    tool_name = "Gitleaks"
    recommended_version = "8.18 latest-release-lock"
    runtime = "windows"
    worker = "WindowsWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = []
    optional_inputs = ["repository_url", "local_path", "config_profile", "redact_secrets", "output_format"]
    expected_evidence = ["secret_findings", "sarif_report", "normalized_json", "redacted_findings"]
    input_schema = {"repository_url": {"type": "string"}, "local_path": {"type": "string"}}
    ai_fillable_inputs = ["redact_secrets", "output_format"]
    panel_fields = [{"name": "repository_url", "label": "Repository URL", "type": "url"}]
    success_markers = ["secret_findings", "redacted_findings"]
    failure_markers = ["missing_gitleaks", "gitleaks_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"secret_findings": "list", "redacted_findings": "list", "sarif_report": "dict"}
    version_lock_id = "m01_osint/gitleaks"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        target = _repo_scan_target(context.parameters)
        tool = _tool_path("gitleaks")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["gitleaks"])
        command = [tool, "detect", "--source", target, "--report-format", "json", "--no-banner"]
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
        normalized = _normalize_secret_scan(result.stdout, "gitleaks", _optional_bool(context.parameters, "redact_secrets", True))
        evidence = _execution_evidence(context, self.technique_id, "gitleaks_json", EVIDENCE_QUALITY_HIGH, "Gitleaks repository scan completed.", normalized, "gitleaks")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class WhatwebFingerprintTechnique(BaseTechnique):
    """Technique 31: WhatWeb passive web technology fingerprinting."""

    technique_id = "osint.whatweb_fingerprint"
    module_id = M01_MODULE_ID
    display_name = "WhatWeb fingerprint"
    description = "Run WhatWeb in passive or operator-selected mode for supplied URLs."
    tool_name = "WhatWeb"
    recommended_version = "0.5.5 latest-release-lock"
    runtime = "wsl2"
    worker = "WSLWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["urls"]
    optional_inputs = ["target", "aggression_profile", "output_format", "include_plugins"]
    expected_evidence = ["technology_fingerprints", "plugin_matches", "normalized_json"]
    input_schema = {"urls": {"type": "array"}, "aggression_profile": {"enum": ["passive", "standard", "deep"]}}
    ai_fillable_inputs = ["aggression_profile", "output_format", "include_plugins"]
    panel_fields = [{"name": "urls", "label": "URLs", "type": "textarea"}]
    success_markers = ["technology_fingerprints", "plugin_matches"]
    failure_markers = ["missing_whatweb", "whatweb_nonzero_exit"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"technology_fingerprints": "list", "plugin_matches": "list"}
    version_lock_id = "m01_osint/whatweb"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        urls = _url_list(context.parameters, "urls")
        tool = _tool_path("whatweb")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["whatweb"])
        aggression = {"passive": "1", "standard": "2", "deep": "3"}[_choice(context.parameters, "aggression_profile", "passive", {"passive", "standard", "deep"})]
        result = _run_command([tool, "--log-json=-", "--aggression", aggression, *urls], _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
        normalized = _normalize_whatweb(result.stdout)
        evidence = _execution_evidence(context, self.technique_id, "whatweb_json", EVIDENCE_QUALITY_HIGH, "WhatWeb fingerprint completed.", normalized, "whatweb")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class WappalyzerFingerprintTechnique(BaseTechnique):
    """Technique 32: Wappalyzer API or CLI technology fingerprinting."""

    technique_id = "osint.wappalyzer_fingerprint"
    module_id = M01_MODULE_ID
    display_name = "Wappalyzer fingerprint"
    description = "Use Wappalyzer API or local CLI for passive web technology fingerprints."
    tool_name = "Wappalyzer CLI/API"
    recommended_version = "latest"
    runtime = "api_or_node"
    worker = "APIWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["urls"]
    optional_inputs = ["api_profile", "include_confidence", "output_format"]
    expected_evidence = ["technology_fingerprints", "confidence_scores", "normalized_json"]
    input_schema = {"urls": {"type": "array"}}
    ai_fillable_inputs = ["include_confidence", "output_format"]
    panel_fields = [{"name": "urls", "label": "URLs", "type": "textarea"}]
    success_markers = ["technology_fingerprints"]
    failure_markers = ["missing_wappalyzer", "wappalyzer_http_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"technology_fingerprints": "list", "confidence_scores": "dict"}
    version_lock_id = "m01_osint/wappalyzer"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        urls = _url_list(context.parameters, "urls")
        api_key = str(context.parameters.get("api_key") or os.environ.get("WAPPALYZER_API_KEY", "")).strip()
        if api_key:
            payloads = [_http_get_json("https://api.wappalyzer.com/v2/lookup/", headers={"x-api-key": api_key}, params={"urls": url}) for url in urls]
            normalized = _normalize_wappalyzer_api([item["payload"] for item in payloads], [str(item["url"]) for item in payloads])
        else:
            tool = _tool_path("wappalyzer")
            if tool is None:
                return _missing_tool_result(self.technique_id, ["wappalyzer"])
            result = _run_command([tool, *urls], _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
            normalized = _normalize_wappalyzer_cli(result.stdout, list(result.command))
        evidence = _execution_evidence(context, self.technique_id, "wappalyzer_json", EVIDENCE_QUALITY_HIGH, "Wappalyzer fingerprint completed.", normalized, "wappalyzer")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class MlLocalFingerprintingTechnique(BaseTechnique):
    """Technique 33: local deterministic banner/header product fingerprinting."""

    technique_id = "osint.ml_local_fingerprinting"
    module_id = M01_MODULE_ID
    display_name = "ML local fingerprinting"
    description = "Classify banner and header text locally using a deterministic signature catalog."
    tool_name = "local_embeddings_model"
    recommended_version = "all-MiniLM-L6-v2 baseline"
    runtime = "local_ai"
    worker = "AIWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["banner_texts"]
    optional_inputs = ["headers", "model_profile", "confidence_threshold", "output_format"]
    expected_evidence = ["predicted_products", "predicted_versions", "confidence_scores", "normalized_json"]
    input_schema = {"banner_texts": {"type": "array"}, "confidence_threshold": {"type": "number"}}
    ai_fillable_inputs = ["model_profile", "confidence_threshold"]
    panel_fields = [{"name": "banner_texts", "label": "Banner texts", "type": "textarea"}]
    success_markers = ["predicted_products", "confidence_scores"]
    failure_markers = ["no_banner_texts"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"predicted_products": "list", "predicted_versions": "list", "confidence_scores": "dict"}
    version_lock_id = "m01_osint/local-fingerprinting"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        banners = _string_list(context.parameters, "banner_texts")
        headers = context.parameters.get("headers", {})
        if not isinstance(headers, dict):
            raise ContractError("headers must be an object when provided.")
        threshold = float(context.parameters.get("confidence_threshold", 0.5))
        normalized = _local_product_fingerprint(banners, {str(k): str(v) for k, v in headers.items()}, threshold)
        evidence = _execution_evidence(context, self.technique_id, "local_fingerprint_json", EVIDENCE_QUALITY_HIGH, "Local product fingerprinting completed.", normalized, "local-fingerprint")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class InternalArpNetbiosTechnique(BaseTechnique):
    """Technique 34: bounded internal ARP/NetBIOS discovery."""

    technique_id = "osint.internal_arp_netbios"
    module_id = M01_MODULE_ID
    display_name = "Internal ARP NetBIOS"
    description = "Collect internal host hints from the local ARP cache or nmap ping/NetBIOS scripts inside confirmed scope."
    tool_name = "nmap NSE + custom scripts"
    recommended_version = "Nmap 7.99"
    runtime = "windows_or_wsl2"
    worker = "WindowsWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["network_range"]
    optional_inputs = ["interface", "discovery_profile", "include_netbios", "output_format"]
    expected_evidence = ["internal_hosts", "netbios_names", "mac_addresses", "normalized_json", "attack_surface_updates"]
    input_schema = {"network_range": {"type": "string"}, "include_netbios": {"type": "boolean"}}
    ai_fillable_inputs = ["discovery_profile", "include_netbios"]
    panel_fields = [{"name": "network_range", "label": "Network range", "type": "text"}]
    success_markers = ["internal_hosts", "mac_addresses"]
    failure_markers = ["missing_nmap", "internal_scope_not_confirmed"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"internal_hosts": "list", "netbios_names": "list", "mac_addresses": "list"}
    version_lock_id = "m01_osint/internal-arp-netbios"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        network = _internal_network_arg(context.parameters)
        include_netbios = _optional_bool(context.parameters, "include_netbios", False)
        nmap_path = _tool_path("nmap")
        if nmap_path is None:
            arp_path = _tool_path("arp")
            if arp_path is None:
                return _missing_tool_result(self.technique_id, ["nmap", "arp"])
            result = _run_command([arp_path, "-a"], _optional_int(context.parameters, "max_duration_seconds", 30, 5, 300))
            normalized = _normalize_arp_cache(result.stdout, network)
        else:
            scripts = ["nbstat"] if include_netbios else []
            command = [nmap_path, "-sn", "-oX", "-", network]
            if scripts:
                command.extend(["--script", ",".join(scripts)])
            result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1800))
            normalized = _normalize_internal_nmap(result.stdout, list(result.command))
        evidence = _execution_evidence(context, self.technique_id, "internal_arp_netbios_json", EVIDENCE_QUALITY_HIGH, "Internal ARP/NetBIOS discovery completed.", normalized, "internal-discovery")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class InternalSmbEnumTechnique(BaseTechnique):
    """Technique 35: read-only SMB metadata enumeration."""

    technique_id = "osint.internal_smb_enum"
    module_id = M01_MODULE_ID
    display_name = "Internal SMB enum"
    description = "Run CrackMapExec SMB read-only enumeration against explicitly supplied internal targets."
    tool_name = "CrackMapExec"
    recommended_version = "6.x latest-release-lock"
    runtime = "wsl2"
    worker = "WSLWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["targets"]
    optional_inputs = ["credential_profile", "enum_profile", "output_format"]
    expected_evidence = ["smb_hosts", "smb_shares", "smb_metadata", "normalized_json"]
    input_schema = {"targets": {"type": "array"}}
    ai_fillable_inputs = ["enum_profile", "output_format"]
    panel_fields = [{"name": "targets", "label": "Targets", "type": "textarea"}]
    success_markers = ["smb_hosts", "smb_metadata"]
    failure_markers = ["missing_crackmapexec", "internal_scope_not_confirmed"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"smb_hosts": "list", "smb_shares": "list", "smb_metadata": "dict"}
    version_lock_id = "m01_osint/crackmapexec-smb"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        targets = _internal_targets(context.parameters)
        tool = _tool_path("crackmapexec") or _tool_path("cme")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["crackmapexec", "cme"])
        profile = _choice(context.parameters, "enum_profile", "hosts", {"shares", "hosts", "users", "standard"})
        command = [tool, "smb", *targets]
        if profile in {"shares", "standard"}:
            command.append("--shares")
        if profile == "users":
            command.append("--users")
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1800))
        normalized = _normalize_cme_smb(result.stdout, list(result.command))
        evidence = _execution_evidence(context, self.technique_id, "internal_smb_enum_text", EVIDENCE_QUALITY_HIGH, "Internal SMB enumeration completed.", normalized, "cme-smb")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class InternalLdapEnumTechnique(BaseTechnique):
    """Technique 36: read-only LDAP enumeration."""

    technique_id = "osint.internal_ldap_enum"
    module_id = M01_MODULE_ID
    display_name = "Internal LDAP enum"
    description = "Run ldapsearch read-only queries for base, user, group, or computer entries."
    tool_name = "ldapsearch"
    recommended_version = "system"
    runtime = "wsl2"
    worker = "WSLWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["ldap_server"]
    optional_inputs = ["base_dn", "credential_profile", "query_profile", "output_format"]
    expected_evidence = ["ldap_entries", "users", "groups", "computers", "normalized_json"]
    input_schema = {"ldap_server": {"type": "string"}, "base_dn": {"type": "string"}}
    ai_fillable_inputs = ["query_profile", "output_format"]
    panel_fields = [{"name": "ldap_server", "label": "LDAP server", "type": "text"}]
    success_markers = ["ldap_entries"]
    failure_markers = ["missing_ldapsearch", "internal_scope_not_confirmed"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"ldap_entries": "list", "users": "list", "groups": "list", "computers": "list"}
    version_lock_id = "m01_osint/ldapsearch"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        server = _require_string(context.parameters, "ldap_server")
        base_dn = str(context.parameters.get("base_dn", "")).strip()
        tool = _tool_path("ldapsearch")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["ldapsearch"])
        profile = _choice(context.parameters, "query_profile", "base", {"base", "users", "groups", "computers", "custom"})
        command = _ldapsearch_command(tool, server, base_dn, profile)
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1800))
        normalized = _normalize_ldif(result.stdout)
        evidence = _execution_evidence(context, self.technique_id, "internal_ldap_ldif", EVIDENCE_QUALITY_HIGH, "Internal LDAP enumeration completed.", normalized, "ldapsearch")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class InternalMssqlEnumTechnique(BaseTechnique):
    """Technique 37: read-only MSSQL service enumeration."""

    technique_id = "osint.internal_mssql_enum"
    module_id = M01_MODULE_ID
    display_name = "Internal MSSQL enum"
    description = "Run CrackMapExec MSSQL discovery against explicitly supplied internal targets."
    tool_name = "CrackMapExec"
    recommended_version = "6.x latest-release-lock"
    runtime = "wsl2"
    worker = "WSLWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["targets"]
    optional_inputs = ["credential_profile", "enum_profile", "output_format"]
    expected_evidence = ["mssql_instances", "mssql_metadata", "normalized_json"]
    input_schema = {"targets": {"type": "array"}}
    ai_fillable_inputs = ["enum_profile", "output_format"]
    panel_fields = [{"name": "targets", "label": "Targets", "type": "textarea"}]
    success_markers = ["mssql_instances"]
    failure_markers = ["missing_crackmapexec", "internal_scope_not_confirmed"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"mssql_instances": "list", "mssql_metadata": "dict"}
    version_lock_id = "m01_osint/crackmapexec-mssql"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        targets = _internal_targets(context.parameters)
        tool = _tool_path("crackmapexec") or _tool_path("cme")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["crackmapexec", "cme"])
        command = [tool, "mssql", *targets]
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1800))
        normalized = _normalize_cme_mssql(result.stdout, list(result.command))
        evidence = _execution_evidence(context, self.technique_id, "internal_mssql_enum_text", EVIDENCE_QUALITY_HIGH, "Internal MSSQL enumeration completed.", normalized, "cme-mssql")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class InternalRdpEnumTechnique(BaseTechnique):
    """Technique 38: read-only RDP script enumeration."""

    technique_id = "osint.internal_rdp_enum"
    module_id = M01_MODULE_ID
    display_name = "Internal RDP enum"
    description = "Run nmap RDP NSE scripts against explicitly supplied internal targets."
    tool_name = "nmap NSE"
    recommended_version = "Nmap 7.99"
    runtime = "windows_or_wsl2"
    worker = "WindowsWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["targets"]
    optional_inputs = ["rdp_profile", "output_format"]
    expected_evidence = ["rdp_services", "security_info", "normalized_json"]
    input_schema = {"targets": {"type": "array"}}
    ai_fillable_inputs = ["rdp_profile", "output_format"]
    panel_fields = [{"name": "targets", "label": "Targets", "type": "textarea"}]
    success_markers = ["rdp_services", "security_info"]
    failure_markers = ["missing_nmap", "internal_scope_not_confirmed"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"rdp_services": "list", "security_info": "dict"}
    version_lock_id = "m01_osint/nmap-rdp-nse"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        return _execute_nmap_service_enum(self, context, "3389", "rdp-enum-encryption", "rdp_services")


class InternalVncEnumTechnique(BaseTechnique):
    """Technique 39: read-only VNC script enumeration."""

    technique_id = "osint.internal_vnc_enum"
    module_id = M01_MODULE_ID
    display_name = "Internal VNC enum"
    description = "Run nmap VNC NSE scripts against explicitly supplied internal targets."
    tool_name = "nmap NSE"
    recommended_version = "Nmap 7.99"
    runtime = "windows_or_wsl2"
    worker = "WindowsWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["targets"]
    optional_inputs = ["vnc_profile", "output_format"]
    expected_evidence = ["vnc_services", "security_info", "normalized_json"]
    input_schema = {"targets": {"type": "array"}}
    ai_fillable_inputs = ["vnc_profile", "output_format"]
    panel_fields = [{"name": "targets", "label": "Targets", "type": "textarea"}]
    success_markers = ["vnc_services", "security_info"]
    failure_markers = ["missing_nmap", "internal_scope_not_confirmed"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"vnc_services": "list", "security_info": "dict"}
    version_lock_id = "m01_osint/nmap-vnc-nse"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        return _execute_nmap_service_enum(self, context, "5900", "vnc-info", "vnc_services")


class BloodhoundPyAdMapTechnique(BaseTechnique):
    """Technique 40: BloodHound.py read-only AD graph collection."""

    technique_id = "osint.bloodhound_py_ad_map"
    module_id = M01_MODULE_ID
    display_name = "BloodHound.py AD map"
    description = "Run BloodHound.py collection using operator-provided domain/DC context and summarize generated graph files."
    tool_name = "BloodHound.py"
    recommended_version = "latest-release-lock"
    runtime = "python_lib_or_wsl2"
    worker = "WSLWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["domain", "output_directory"]
    optional_inputs = ["dc_host", "credential_profile", "collection_profile"]
    expected_evidence = ["ad_graph_files", "users", "groups", "computers", "relationships", "normalized_json"]
    input_schema = {"domain": {"type": "string"}, "output_directory": {"type": "string"}}
    ai_fillable_inputs = ["collection_profile"]
    panel_fields = [{"name": "domain", "label": "Domain", "type": "text"}]
    success_markers = ["ad_graph_files", "relationships"]
    failure_markers = ["missing_bloodhound_py", "internal_scope_not_confirmed"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"ad_graph_files": "list", "users": "list", "groups": "list", "computers": "list"}
    version_lock_id = "m01_osint/bloodhound-py"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        domain = _require_string(context.parameters, "domain")
        output_dir = Path(_require_string(context.parameters, "output_directory"))
        output_dir.mkdir(parents=True, exist_ok=True)
        tool = _tool_path("bloodhound-python") or _tool_path("bloodhound.py")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["bloodhound-python"])
        collection = _choice(context.parameters, "collection_profile", "default", {"default", "session", "acl", "objectprops", "custom"})
        command = [tool, "-d", domain, "-c", "Default" if collection == "default" else collection, "--zip", "-ns", str(context.parameters.get("dc_host") or domain), "--outputdirectory", output_dir.as_posix()]
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 3600))
        normalized = _normalize_bloodhound_output(output_dir, list(result.command))
        evidence = _execution_evidence(context, self.technique_id, "bloodhound_ad_graph", EVIDENCE_QUALITY_HIGH, "BloodHound.py AD map completed.", normalized, "bloodhound-python")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class LdapsearchAdMapTechnique(InternalLdapEnumTechnique):
    """Technique 41: ldapsearch Active Directory map."""

    technique_id = "osint.ldapsearch_ad_map"
    display_name = "ldapsearch AD map"
    description = "Run ldapsearch read-only Active Directory collection profiles."
    required_inputs = ["ldap_server"]
    optional_inputs = ["base_dn", "credential_profile", "collection_profile", "output_format"]
    expected_evidence = ["ad_entries", "users", "groups", "computers", "normalized_json"]
    ai_fillable_inputs = ["collection_profile", "output_format"]
    success_markers = ["ad_entries"]
    evidence_schema = {"ad_entries": "list", "users": "list", "groups": "list", "computers": "list"}
    version_lock_id = "m01_osint/ldapsearch-ad-map"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_internal_scope(context)
        server = _require_string(context.parameters, "ldap_server")
        base_dn = str(context.parameters.get("base_dn", "")).strip()
        tool = _tool_path("ldapsearch")
        if tool is None:
            return _missing_tool_result(self.technique_id, ["ldapsearch"])
        profile = _choice(context.parameters, "collection_profile", "users", {"users", "groups", "computers", "spns", "custom"})
        command = _ldapsearch_command(tool, server, base_dn, profile)
        result = _run_command(command, _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1800))
        normalized = _normalize_ldif(result.stdout)
        normalized["ad_entries"] = normalized["ldap_entries"]
        evidence = _execution_evidence(context, self.technique_id, "ldapsearch_ad_ldif", EVIDENCE_QUALITY_HIGH, "ldapsearch AD map completed.", normalized, "ldapsearch")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class X4EngineIntegrationTechnique(BaseTechnique):
    """Technique 42: read-only extraction through a configured source URL."""

    technique_id = "scraping.x4_engine_integration"
    module_id = M01_MODULE_ID
    display_name = "X4 engine integration"
    description = "Fetch an operator-supplied public source and extract tabular/link/text rows matching a natural-language query."
    tool_name = "X4 internal engine"
    recommended_version = "internal"
    runtime = "x4_connector"
    worker = "X4ConnectorWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["natural_language_query"]
    optional_inputs = ["base_url", "source_profile", "selector_profile", "export_format", "preview_enabled"]
    expected_evidence = ["extracted_rows", "source_urls", "normalized_json", "export_path"]
    input_schema = {"natural_language_query": {"type": "string"}, "base_url": {"type": "string"}}
    ai_fillable_inputs = ["source_profile", "selector_profile", "export_format"]
    panel_fields = [{"name": "natural_language_query", "label": "Query", "type": "text"}]
    success_markers = ["extracted_rows", "source_urls"]
    failure_markers = ["missing_base_url", "x4_fetch_error"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = True
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"extracted_rows": "list", "source_urls": "list", "export_path": "string"}
    version_lock_id = "m01_osint/x4-engine-reference"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        query = _require_string(context.parameters, "natural_language_query")
        base_url = _require_url(context.parameters, "base_url")
        response = requests.get(base_url, timeout=20, headers={"user-agent": "ojo-de-dios-m01-x4"})
        if response.status_code >= 400:
            raise ContractError(f"X4 source fetch failed with HTTP {response.status_code}.")
        normalized = _extract_rows_from_html(response.text, base_url, query, _optional_bool(context.parameters, "preview_enabled", True))
        evidence = _execution_evidence(context, self.technique_id, "x4_extraction_json", EVIDENCE_QUALITY_HIGH, "X4-style extraction completed.", normalized, "x4-reference")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class X5IntelligentPlannerTechnique(BaseTechnique):
    """Technique 43: deterministic local scraping planner."""

    technique_id = "scraping.x5_intelligent_planner"
    module_id = M01_MODULE_ID
    display_name = "X5 intelligent planner"
    description = "Build a local, deterministic scraping plan from source candidates and a requested output schema."
    tool_name = "X5 + Dolphin Mistral Nemo 12B"
    recommended_version = "internal"
    runtime = "x5_planner"
    worker = "X5PlannerWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["user_goal", "source_candidates"]
    optional_inputs = ["depth_limit", "data_schema", "output_format"]
    expected_evidence = ["scraping_plan", "source_priorities", "planned_steps", "normalized_json"]
    input_schema = {"user_goal": {"type": "string"}, "source_candidates": {"type": "array"}}
    ai_fillable_inputs = ["source_candidates", "depth_limit", "data_schema"]
    panel_fields = [{"name": "user_goal", "label": "Goal", "type": "text"}]
    success_markers = ["scraping_plan", "planned_steps"]
    failure_markers = ["missing_source_candidates"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"scraping_plan": "dict", "source_priorities": "list", "planned_steps": "list"}
    version_lock_id = "m01_osint/x5-planner-reference"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        goal = _require_string(context.parameters, "user_goal")
        sources = _url_candidates(context.parameters, "source_candidates")
        schema = context.parameters.get("data_schema", {})
        if schema and not isinstance(schema, dict):
            raise ContractError("data_schema must be an object when provided.")
        normalized = _build_scraping_plan(goal, sources, _optional_int(context.parameters, "depth_limit", 1, 1, 5), schema if isinstance(schema, dict) else {})
        evidence = _execution_evidence(context, self.technique_id, "x5_scraping_plan_json", EVIDENCE_QUALITY_HIGH, "X5 scraping plan generated.", normalized, "x5-planner")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class CaptchaTextSolverAiTechnique(BaseTechnique):
    """Technique 44: text challenge summarization with mandatory manual review support."""

    technique_id = "scraping.captcha_text_solver_ai"
    module_id = M01_MODULE_ID
    display_name = "Captcha text solver AI"
    description = "Analyze text-only challenges locally and return confidence/manual-review status without browser automation."
    tool_name = "Dolphin Mistral Nemo 12B"
    recommended_version = "local_model"
    runtime = "local_ai"
    worker = "AIWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["challenge_text", "source_context"]
    optional_inputs = ["confidence_threshold", "manual_review_enabled"]
    expected_evidence = ["challenge_summary", "solver_confidence", "answer_candidate", "manual_required_status"]
    input_schema = {"challenge_text": {"type": "string"}, "source_context": {"type": "string"}}
    ai_fillable_inputs = ["challenge_text", "source_context"]
    panel_fields = [{"name": "challenge_text", "label": "Challenge", "type": "textarea"}]
    success_markers = ["challenge_summary", "manual_required_status"]
    failure_markers = ["manual_review_required"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"challenge_summary": "dict", "solver_confidence": "number", "answer_candidate": "string"}
    version_lock_id = "m01_osint/captcha-text-review"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        challenge = _require_string(context.parameters, "challenge_text")
        source_context = _require_string(context.parameters, "source_context")
        threshold = float(context.parameters.get("confidence_threshold", 0.9))
        normalized = _solve_text_challenge_for_review(challenge, source_context, threshold, _optional_bool(context.parameters, "manual_review_enabled", True))
        evidence = _execution_evidence(context, self.technique_id, "captcha_text_review_json", EVIDENCE_QUALITY_HIGH, "Text challenge review completed.", normalized, "local-review")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class CaptchaVisualBypassTechnique(BaseTechnique):
    """Technique 45: OCR-only visual challenge evidence capture; no automated submission."""

    technique_id = "scraping.captcha_visual_bypass"
    module_id = M01_MODULE_ID
    display_name = "Captcha visual OCR review"
    description = "Run OCR over an operator-supplied screenshot and require manual review; it does not bypass or submit challenges."
    tool_name = "Playwright + Tesseract OCR"
    recommended_version = "latest-release-lock"
    runtime = "browser_automation"
    worker = "BrowserAutomationWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["page_url"]
    optional_inputs = ["screenshot_path", "ocr_profile", "browser_profile", "manual_review_enabled"]
    expected_evidence = ["screenshot_hash", "ocr_output", "confidence", "manual_required_status"]
    input_schema = {"page_url": {"type": "string"}, "screenshot_path": {"type": "string"}}
    ai_fillable_inputs = ["ocr_profile", "manual_review_enabled"]
    panel_fields = [{"name": "page_url", "label": "Page URL", "type": "url"}]
    success_markers = ["ocr_output", "manual_required_status"]
    failure_markers = ["missing_tesseract", "missing_screenshot"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"screenshot_hash": "string", "ocr_output": "string", "confidence": "number"}
    version_lock_id = "m01_osint/captcha-visual-ocr"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_confirmed(context)
        page_url = _require_url(context.parameters, "page_url")
        screenshot = Path(_require_string(context.parameters, "screenshot_path"))
        if not screenshot.is_file():
            raise ContractError("screenshot_path must point to an existing image file.")
        tesseract = _tool_path("tesseract")
        if tesseract is None:
            return _missing_tool_result(self.technique_id, ["tesseract"])
        result = _run_command([tesseract, screenshot.as_posix(), "stdout"], _optional_int(context.parameters, "max_duration_seconds", 30, 5, 300))
        normalized = _normalize_visual_ocr(page_url, screenshot, result.stdout)
        evidence = _execution_evidence(context, self.technique_id, "captcha_visual_ocr_json", EVIDENCE_QUALITY_HIGH, "Visual challenge OCR completed for manual review.", normalized, "tesseract")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class ProxyRotationSimTechnique(BaseTechnique):
    """Technique 46: offline proxy rotation simulation and status normalization."""

    technique_id = "scraping.proxy_rotation_sim"
    module_id = M01_MODULE_ID
    display_name = "Proxy rotation simulation"
    description = "Generate a local rotation schedule and normalize operator-provided connection observations; no proxy connections are opened."
    tool_name = "proxies SOCKS5 + double SIM profile"
    recommended_version = "internal"
    runtime = "network_profile"
    worker = "ScrapingWorker"
    permission_level = PERMISSION_ACTIVE_LOW
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["proxy_profile", "rotation_strategy", "connection_profile"]
    optional_inputs = ["cooldown_seconds", "max_failures"]
    expected_evidence = ["proxy_usage_log", "rotation_events", "connection_status", "normalized_json"]
    input_schema = {"proxy_profile": {"type": "string"}, "rotation_strategy": {"enum": ["manual", "timed", "failure_based", "custom"]}}
    ai_fillable_inputs = ["rotation_strategy", "cooldown_seconds", "max_failures"]
    panel_fields = [{"name": "proxy_profile", "label": "Proxy profile", "type": "text"}]
    success_markers = ["rotation_events", "connection_status"]
    failure_markers = ["invalid_rotation_profile"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"proxy_usage_log": "list", "rotation_events": "list", "connection_status": "dict"}
    version_lock_id = "m01_osint/proxy-rotation-sim"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        _ensure_confirmed(context)
        normalized = _simulate_proxy_rotation(_require_string(context.parameters, "proxy_profile"), _choice(context.parameters, "rotation_strategy", "manual", {"manual", "timed", "failure_based", "custom"}), _optional_int(context.parameters, "cooldown_seconds", 60, 0, 86400), _optional_int(context.parameters, "max_failures", 3, 1, 100), _require_string(context.parameters, "connection_profile"))
        evidence = _execution_evidence(context, self.technique_id, "proxy_rotation_sim_json", EVIDENCE_QUALITY_HIGH, "Proxy rotation simulation completed.", normalized, "local-sim")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


class RecursiveAiDiscoveryTechnique(BaseTechnique):
    """Technique 47: deterministic recursive source discovery over supplied seed results."""

    technique_id = "scraping.recursive_ai_discovery"
    module_id = M01_MODULE_ID
    display_name = "Recursive AI discovery"
    description = "Expand supplied seed results into bounded source candidates and structured records without fabricating evidence."
    tool_name = "Dolphin Mistral Nemo 12B + X4"
    recommended_version = "internal"
    runtime = "local_ai_x4"
    worker = "ScrapingWorker"
    permission_level = PERMISSION_PASSIVE
    risk_level = "low"
    noise_level = "low"
    required_inputs = ["seed_results", "discovery_goal"]
    optional_inputs = ["max_iterations", "source_rules", "stop_conditions"]
    expected_evidence = ["discovered_sources", "iteration_log", "structured_results", "normalized_json"]
    input_schema = {"seed_results": {"type": "object"}, "discovery_goal": {"type": "string"}}
    ai_fillable_inputs = ["discovery_goal", "source_rules", "stop_conditions"]
    panel_fields = [{"name": "discovery_goal", "label": "Discovery goal", "type": "text"}]
    success_markers = ["discovered_sources", "iteration_log"]
    failure_markers = ["empty_seed_results"]
    demo_behavior = {"real_execution": False}
    dry_run_behavior = {"validate_inputs": True}
    requires_network = False
    implementation_status = STATUS_READY_CONTROLLED
    requires_user_implementation = False
    evidence_schema = {"discovered_sources": "list", "iteration_log": "list", "structured_results": "list"}
    version_lock_id = "m01_osint/recursive-ai-discovery"

    def execute(self, context: TechniqueExecutionContext) -> TechniqueExecutionResult:
        seed = context.parameters.get("seed_results")
        if not isinstance(seed, dict) or not seed:
            raise ContractError("seed_results must be a non-empty object.")
        goal = _require_string(context.parameters, "discovery_goal")
        rules = context.parameters.get("source_rules", {})
        if rules and not isinstance(rules, dict):
            raise ContractError("source_rules must be an object when provided.")
        normalized = _recursive_discovery(seed, goal, _optional_int(context.parameters, "max_iterations", 2, 1, 10), rules if isinstance(rules, dict) else {}, _string_list(context.parameters, "stop_conditions"))
        evidence = _execution_evidence(context, self.technique_id, "recursive_discovery_json", EVIDENCE_QUALITY_HIGH, "Recursive discovery completed.", normalized, "local-recursive-discovery")
        return TechniqueExecutionResult(self.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)

def _require_url(parameters: dict[str, Any], name: str) -> str:
    url = _require_string(parameters, name)
    if not url.startswith(("http://", "https://")):
        raise ContractError(f"{name} must be an http(s) URL.")
    return url


def _url_candidates(parameters: dict[str, Any], name: str) -> list[str]:
    values = _string_list(parameters, name)
    if not values:
        raise ContractError(f"{name} must include at least one URL candidate.")
    invalid = [value for value in values if not value.startswith(("http://", "https://"))]
    if invalid:
        raise ContractError(f"{name} contains non-http(s) URL candidates.")
    return values


def _extract_rows_from_html(html_text: str, source_url: str, query: str, preview_enabled: bool) -> dict[str, Any]:
    import html.parser

    class RowParser(html.parser.HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.links: list[dict[str, str]] = []
            self.text_parts: list[str] = []
            self._href: str | None = None

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag == "a":
                self._href = next((value for key, value in attrs if key == "href" and value), None)

        def handle_endtag(self, tag: str) -> None:
            if tag == "a":
                self._href = None

        def handle_data(self, data: str) -> None:
            text = data.strip()
            if not text:
                return
            self.text_parts.append(text)
            if self._href:
                self.links.append({"text": text, "url": self._href})

    parser = RowParser()
    parser.feed(html_text)
    query_terms = {term.lower() for term in query.split() if len(term) > 2}
    rows = []
    for index, text in enumerate(parser.text_parts):
        lower = text.lower()
        if not query_terms or any(term in lower for term in query_terms):
            rows.append({"row_index": index, "text": text[:500], "source_url": source_url})
    for link in parser.links:
        rows.append({"row_index": len(rows), "text": link["text"][:500], "url": link["url"], "source_url": source_url})
    return {"extracted_rows": rows[:50] if preview_enabled else rows, "source_urls": [source_url], "export_path": None, "row_count": len(rows)}


def _build_scraping_plan(goal: str, sources: list[str], depth_limit: int, schema: dict[str, Any]) -> dict[str, Any]:
    priorities = [{"source_url": url, "priority": index + 1, "reason": "operator_candidate_order"} for index, url in enumerate(sources)]
    fields = list(schema) if schema else ["title", "url", "summary"]
    steps = []
    for priority in priorities:
        steps.append({"step": "fetch", "source_url": priority["source_url"], "depth": 0})
        steps.append({"step": "extract", "source_url": priority["source_url"], "fields": fields})
        if depth_limit > 1:
            steps.append({"step": "discover_links", "source_url": priority["source_url"], "max_depth": depth_limit - 1})
    return {"scraping_plan": {"goal": goal, "depth_limit": depth_limit, "schema_fields": fields}, "source_priorities": priorities, "planned_steps": steps}


def _solve_text_challenge_for_review(challenge: str, source_context: str, threshold: float, manual_review_enabled: bool) -> dict[str, Any]:
    answer = None
    confidence = 0.0
    stripped = challenge.strip().lower()
    if "+" in stripped and all(part.strip().isdigit() for part in stripped.replace("?", "").split("+") if part.strip()):
        numbers = [int(part.strip()) for part in stripped.replace("?", "").split("+") if part.strip()]
        answer = str(sum(numbers))
        confidence = 0.95
    elif "type" in stripped and "word" in stripped:
        answer = challenge.split()[-1].strip(".?!'")
        confidence = 0.6
    manual_required = manual_review_enabled or confidence < threshold
    return {"challenge_summary": {"length": len(challenge), "source_context": source_context[:200], "method": "deterministic_text_review"}, "solver_confidence": confidence, "answer_candidate": answer, "manual_required_status": "REQUIRED" if manual_required else "NOT_REQUIRED"}


def _normalize_visual_ocr(page_url: str, screenshot: Path, ocr_output: str) -> dict[str, Any]:
    content = screenshot.read_bytes()
    text = ocr_output.strip()
    confidence = min(0.9, 0.2 + (len(text) / 100)) if text else 0.0
    return {"page_url": page_url, "screenshot_hash": hashlib.sha256(content).hexdigest(), "ocr_output": text, "confidence": confidence, "manual_required_status": "REQUIRED"}


def _simulate_proxy_rotation(proxy_profile: str, strategy: str, cooldown_seconds: int, max_failures: int, connection_profile: str) -> dict[str, Any]:
    events = []
    for index in range(max(1, min(max_failures, 5))):
        events.append({"event_index": index, "strategy": strategy, "cooldown_seconds": cooldown_seconds, "action": "rotate_after_failure" if strategy == "failure_based" else "scheduled_rotation" if strategy == "timed" else "manual_review"})
    return {"proxy_usage_log": [], "rotation_events": events, "connection_status": {"profile": connection_profile, "proxy_profile": proxy_profile, "opened_connections": 0, "simulation_only": True}}


def _recursive_discovery(seed: dict[str, Any], goal: str, max_iterations: int, source_rules: dict[str, Any], stop_conditions: list[str]) -> dict[str, Any]:
    discovered: list[str] = []
    structured: list[dict[str, Any]] = []
    log = []
    frontier = _collect_urls(seed)
    for iteration in range(max_iterations):
        new_urls = [url for url in frontier if url not in discovered]
        discovered.extend(new_urls)
        structured.extend({"source_url": url, "goal": goal, "rules_applied": sorted(source_rules)} for url in new_urls)
        log.append({"iteration": iteration + 1, "new_sources": new_urls, "stop_conditions": stop_conditions})
        frontier = []
        if not new_urls or any(condition == "no_new_sources" for condition in stop_conditions):
            break
    return {"discovered_sources": discovered, "iteration_log": log, "structured_results": structured}


def _collect_urls(value: Any) -> list[str]:
    urls: list[str] = []
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        urls.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            urls.extend(_collect_urls(item))
    elif isinstance(value, list):
        for item in value:
            urls.extend(_collect_urls(item))
    return sorted(set(urls))

def _ensure_internal_scope(context: TechniqueExecutionContext) -> None:
    _ensure_confirmed(context)
    if context.parameters.get("internal_scope_confirmed") is not True:
        raise ContractError("internal_scope_confirmed must be true for internal network discovery.")


def _internal_network_arg(parameters: dict[str, Any]) -> str:
    value = _require_string(parameters, "network_range")
    try:
        network = ip_network(value, strict=False)
    except ValueError as error:
        raise ContractError("network_range must be a valid IP/CIDR range.") from error
    if not (network.is_private or network.is_loopback or network.is_link_local):
        raise ContractError("network_range must be private, loopback, or link-local internal scope.")
    return str(network)


def _internal_targets(parameters: dict[str, Any]) -> list[str]:
    targets = _string_list(parameters, "targets")
    if not targets:
        raise ContractError("targets must include at least one target.")
    for value in targets:
        try:
            addr = ip_address(value.split(":", 1)[0])
        except ValueError as error:
            raise ContractError("internal targets must be IP addresses for read-only internal enumeration.") from error
        if not (addr.is_private or addr.is_loopback or addr.is_link_local):
            raise ContractError("internal targets must be private, loopback, or link-local addresses.")
    return targets


def _normalize_arp_cache(stdout: str, network: str) -> dict[str, Any]:
    hosts = []
    macs = []
    for line in _text_lines(stdout):
        tokens = line.replace("(", " ").replace(")", " ").split()
        ip_value = next((token for token in tokens if _is_ip(token)), None)
        mac_value = next((token for token in tokens if ":" in token and len(token.replace(":", "")) == 12), None)
        if ip_value:
            hosts.append({"ip": ip_value, "source": "arp_cache", "mac": mac_value})
        if mac_value:
            macs.append(mac_value.lower())
    return {"network_range": network, "internal_hosts": hosts, "netbios_names": [], "mac_addresses": sorted(set(macs)), "attack_surface_updates": [{"type": "InternalHostNode", "ip": item["ip"]} for item in hosts]}


def _normalize_internal_nmap(stdout: str, command: list[str]) -> dict[str, Any]:
    hosts = []
    names = []
    macs = []
    ports = _parse_nmap_xml_ports(stdout) if stdout.strip().startswith("<") else []
    if stdout.strip().startswith("<"):
        import xml.etree.ElementTree as ET
        root = ET.fromstring(stdout)
        for host in root.findall("host"):
            address = ""
            for addr in host.findall("address"):
                if addr.attrib.get("addrtype") in {"ipv4", "ipv6"}:
                    address = addr.attrib.get("addr", "")
                if addr.attrib.get("addrtype") == "mac" and addr.attrib.get("addr"):
                    macs.append(str(addr.attrib["addr"]).lower())
            for hostname in host.findall("./hostnames/hostname"):
                name = hostname.attrib.get("name")
                if name:
                    names.append(name)
            if address:
                hosts.append({"ip": address, "source": "nmap_ping", "status": "up"})
    return {"internal_hosts": hosts, "netbios_names": sorted(set(names)), "mac_addresses": sorted(set(macs)), "service_fingerprints": ports, "attack_surface_updates": [{"type": "InternalHostNode", "ip": item["ip"]} for item in hosts], "command": command}


def _normalize_cme_smb(stdout: str, command: list[str]) -> dict[str, Any]:
    hosts = []
    shares = []
    for line in _text_lines(stdout):
        parts = line.split()
        ip_value = next((part for part in parts if _is_ip(part)), None)
        if ip_value:
            hosts.append({"ip": ip_value, "raw": line[:500]})
        if "READ" in line or "WRITE" in line:
            share = parts[-2] if len(parts) >= 2 else "unknown"
            shares.append({"host": ip_value, "share": share, "access": "READ_WRITE" if "WRITE" in line else "READ"})
    return {"smb_hosts": hosts, "smb_shares": shares, "smb_metadata": {"host_count": len(hosts), "share_count": len(shares)}, "command": command}


def _normalize_cme_mssql(stdout: str, command: list[str]) -> dict[str, Any]:
    instances = []
    for line in _text_lines(stdout):
        parts = line.split()
        ip_value = next((part for part in parts if _is_ip(part)), None)
        if ip_value:
            instances.append({"ip": ip_value, "raw": line[:500]})
    return {"mssql_instances": instances, "mssql_metadata": {"instance_count": len(instances)}, "command": command}


def _ldapsearch_command(tool: str, server: str, base_dn: str, profile: str) -> list[str]:
    filters = {
        "base": "(objectClass=*)",
        "users": "(&(objectClass=user)(!(objectClass=computer)))",
        "groups": "(objectClass=group)",
        "computers": "(objectClass=computer)",
        "spns": "(servicePrincipalName=*)",
        "custom": "(objectClass=*)",
    }
    command = [tool, "-x", "-H", server]
    if base_dn:
        command.extend(["-b", base_dn])
    command.append(filters[profile])
    return command


def _normalize_ldif(stdout: str) -> dict[str, Any]:
    entries = []
    current: dict[str, Any] = {}
    for line in stdout.splitlines():
        if not line.strip():
            if current:
                entries.append(current)
                current = {}
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if key in current:
            if not isinstance(current[key], list):
                current[key] = [current[key]]
            current[key].append(value)
        else:
            current[key] = value
    if current:
        entries.append(current)
    users = [item for item in entries if _entry_has_class(item, "user") and not _entry_has_class(item, "computer")]
    groups = [item for item in entries if _entry_has_class(item, "group")]
    computers = [item for item in entries if _entry_has_class(item, "computer")]
    return {"ldap_entries": entries, "users": users, "groups": groups, "computers": computers}


def _entry_has_class(entry: dict[str, Any], value: str) -> bool:
    classes = entry.get("objectClass", [])
    if isinstance(classes, str):
        classes = [classes]
    return value.lower() in {str(item).lower() for item in classes}


def _execute_nmap_service_enum(technique: BaseTechnique, context: TechniqueExecutionContext, port: str, script: str, evidence_key: str) -> TechniqueExecutionResult:
    targets = _internal_targets(context.parameters)
    tool = _tool_path("nmap")
    if tool is None:
        return _missing_tool_result(technique.technique_id, ["nmap"])
    result = _run_command([tool, "-sT", "-p", port, "--script", script, "-oX", "-", *targets], _optional_int(context.parameters, "max_duration_seconds", DEFAULT_TIMEOUT_SECONDS, 5, 1800))
    services = _parse_nmap_xml_ports(result.stdout) if result.stdout.strip().startswith("<") else []
    normalized = {evidence_key: services, "security_info": _nmap_script_outputs(result.stdout), "command": list(result.command)}
    evidence = _execution_evidence(context, technique.technique_id, f"{evidence_key}_nmap_xml", EVIDENCE_QUALITY_HIGH, f"Internal {evidence_key} enumeration completed.", normalized, "nmap-nse")
    return TechniqueExecutionResult(technique.technique_id, M01_MODULE_ID, RESULT_SUCCESS, evidence.summary, [evidence], normalized)


def _nmap_script_outputs(stdout: str) -> dict[str, Any]:
    outputs = []
    if not stdout.strip().startswith("<"):
        return {"script_outputs": outputs}
    import xml.etree.ElementTree as ET
    root = ET.fromstring(stdout)
    for script in root.findall(".//script"):
        outputs.append({"id": script.attrib.get("id"), "output": script.attrib.get("output")})
    return {"script_outputs": outputs}


def _normalize_bloodhound_output(output_dir: Path, command: list[str]) -> dict[str, Any]:
    files = []
    users = []
    groups = []
    computers = []
    relationships = []
    for path in sorted(output_dir.glob("*.json")) + sorted(output_dir.glob("*.zip")):
        files.append({"path": path.as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size_bytes": path.stat().st_size})
        if path.suffix == ".json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            lower = path.name.lower()
            data = payload.get("data", []) if isinstance(payload, dict) else []
            if "user" in lower:
                users.extend(data if isinstance(data, list) else [])
            elif "group" in lower:
                groups.extend(data if isinstance(data, list) else [])
            elif "computer" in lower:
                computers.extend(data if isinstance(data, list) else [])
            elif "edge" in lower or "session" in lower:
                relationships.extend(data if isinstance(data, list) else [])
    return {"ad_graph_files": files, "users": users, "groups": groups, "computers": computers, "relationships": relationships, "command": command}

def _search_provider_payload(api_key: str, query: str, limit: int, cx: str = "") -> dict[str, Any]:
    if cx:
        return _http_get_json("https://www.googleapis.com/customsearch/v1", params={"key": api_key, "cx": cx, "q": query, "num": min(limit, 10)})
    return _http_get_json("https://serpapi.com/search.json", params={"api_key": api_key, "engine": "google", "q": query, "num": limit})


def _normalize_social_search(payload: dict[str, Any], source_url: str, platform: str, query: str, query_type: str, redact: bool) -> dict[str, Any]:
    search = _normalize_search_results(payload, source_url)
    social_profiles: list[dict[str, Any]] = []
    company_profiles: list[dict[str, Any]] = []
    hints: list[dict[str, Any]] = []
    for item in search["search_results"]:
        url = str(item.get("url") or "")
        title = str(item.get("title") or "")
        record = {"platform": platform, "url": url, "title": title, "query_type": query_type}
        if "company" in url or query_type == "company":
            company_profiles.append(record)
        else:
            social_profiles.append(record)
        hints.append({"source": query if not redact else _redact_email(query) if "@" in query else query, "target_url": url, "relationship": "public_search_match"})
    return {"social_profiles": social_profiles, "company_profiles": company_profiles, "relationship_hints": hints, "source_urls": search["source_urls"]}


def _normalize_twitter_api(payload: dict[str, Any], source_url: str, query: str, redact: bool) -> dict[str, Any]:
    mentions = []
    hints = []
    for item in payload.get("data", []) if isinstance(payload.get("data", []), list) else []:
        if not isinstance(item, dict):
            continue
        mentions.append({"id": item.get("id"), "author_id": item.get("author_id"), "created_at": item.get("created_at"), "text": item.get("text")})
        hints.append({"source": _redact_email(query) if redact and "@" in query else query, "target": item.get("author_id"), "relationship": "tweet_match"})
    return {"social_profiles": [], "mentions": mentions, "relationship_hints": hints, "source_urls": [source_url]}


def _normalize_github_search(payloads: list[dict[str, Any]], source_urls: list[str], query_type: str) -> dict[str, Any]:
    profiles: list[dict[str, Any]] = []
    repos: list[dict[str, Any]] = []
    exposed: list[dict[str, Any]] = []
    for payload in payloads:
        for item in payload.get("items", []) if isinstance(payload.get("items", []), list) else []:
            if not isinstance(item, dict):
                continue
            if "html_url" in item and "full_name" not in item:
                profiles.append({"login": item.get("login"), "url": item.get("html_url"), "type": item.get("type"), "query_type": query_type})
            if "full_name" in item:
                repo = {"full_name": item.get("full_name"), "url": item.get("html_url"), "description": item.get("description"), "language": item.get("language")}
                repos.append(repo)
                exposed.append({"repository": item.get("full_name"), "url": item.get("html_url"), "reference_type": "repository_search_match"})
    return {"github_profiles": profiles, "repositories": repos, "exposed_references": exposed, "source_urls": source_urls}


def _repo_scan_target(parameters: dict[str, Any]) -> str:
    local_path = str(parameters.get("local_path", "")).strip()
    repository_url = str(parameters.get("repository_url", "")).strip()
    if local_path:
        path = Path(local_path)
        if not path.exists():
            raise ContractError("local_path must exist for repository leak scanning.")
        return path.as_posix()
    if repository_url.startswith(("https://", "ssh://", "git@")):
        return repository_url
    raise ContractError("repository_url or local_path is required for repository leak scanning.")


def _normalize_secret_scan(stdout: str, scanner: str, redact: bool) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for item in _json_lines(stdout):
        detector = item.get("DetectorName") or item.get("RuleID") or item.get("rule")
        raw_secret = str(item.get("Raw") or item.get("Secret") or item.get("secret") or "")
        finding = {
            "scanner": scanner,
            "detector": detector,
            "file": item.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file") if isinstance(item.get("SourceMetadata"), dict) else item.get("File") or item.get("file"),
            "line": item.get("StartLine") or item.get("line"),
            "verified": bool(item.get("Verified", False)),
            "secret_sha256": hashlib.sha256(raw_secret.encode("utf-8")).hexdigest() if raw_secret else None,
            "secret": "[REDACTED]" if redact and raw_secret else raw_secret or None,
        }
        findings.append(finding)
    if not findings:
        try:
            payload = json.loads(stdout) if stdout.strip() else []
        except json.JSONDecodeError:
            payload = []
        for item in payload if isinstance(payload, list) else []:
            if isinstance(item, dict):
                secret = str(item.get("Secret") or item.get("secret") or "")
                findings.append({"scanner": scanner, "detector": item.get("RuleID"), "file": item.get("File"), "line": item.get("StartLine"), "verified": False, "secret_sha256": hashlib.sha256(secret.encode()).hexdigest() if secret else None, "secret": "[REDACTED]" if redact and secret else secret or None})
    return {"secret_findings": findings, "redacted_findings": findings, "raw_output_path": None, "sarif_report": {}, "finding_count": len(findings)}


def _url_list(parameters: dict[str, Any], name: str) -> list[str]:
    urls = _string_list(parameters, name)
    valid = [url for url in urls if url.startswith(("http://", "https://"))]
    if not valid or len(valid) != len(urls):
        raise ContractError(f"{name} must contain http(s) URLs.")
    return valid


def _normalize_whatweb(stdout: str) -> dict[str, Any]:
    payload = json.loads(stdout) if stdout.strip().startswith("[") else _json_lines(stdout)
    if isinstance(payload, dict):
        payload = [payload]
    fingerprints = []
    plugins = []
    for item in payload if isinstance(payload, list) else []:
        if not isinstance(item, dict):
            continue
        target = item.get("target") or item.get("url")
        for name, details in (item.get("plugins") or {}).items() if isinstance(item.get("plugins"), dict) else []:
            plugins.append({"url": target, "plugin": name, "details": details})
            fingerprints.append({"url": target, "product": name, "version": _plugin_version(details), "source": "whatweb"})
    return {"technology_fingerprints": fingerprints, "plugin_matches": plugins}


def _plugin_version(details: Any) -> str | None:
    if isinstance(details, dict):
        version = details.get("version") or details.get("versions")
        if isinstance(version, list):
            return str(version[0]) if version else None
        return str(version) if version else None
    return None


def _normalize_wappalyzer_api(payloads: list[Any], source_urls: list[str]) -> dict[str, Any]:
    fingerprints = []
    confidence: dict[str, float] = {}
    for payload in payloads:
        entries = payload if isinstance(payload, list) else payload.get("technologies", []) if isinstance(payload, dict) else []
        for item in entries if isinstance(entries, list) else []:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or item.get("technology") or "").strip()
            if not name:
                continue
            score = float(item.get("confidence", 100)) / 100 if float(item.get("confidence", 100)) > 1 else float(item.get("confidence", 1))
            fingerprints.append({"product": name, "version": item.get("version"), "categories": item.get("categories", []), "source": "wappalyzer"})
            confidence[name] = score
    return {"technology_fingerprints": fingerprints, "confidence_scores": confidence, "source_urls": source_urls}


def _normalize_wappalyzer_cli(stdout: str, command: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        payload = []
    normalized = _normalize_wappalyzer_api(payload if isinstance(payload, list) else [payload], [])
    normalized["command"] = command
    return normalized


def _local_product_fingerprint(banners: list[str], headers: dict[str, str], threshold: float) -> dict[str, Any]:
    signatures = {
        "nginx": ["nginx"],
        "apache": ["apache", "httpd"],
        "iis": ["microsoft-iis", "iis"],
        "openssh": ["openssh", "ssh-2.0"],
        "express": ["x-powered-by: express", "express"],
        "wordpress": ["wp-content", "wordpress"],
        "cloudflare": ["cloudflare", "cf-ray"],
    }
    corpus = "\n".join(banners + [f"{k}: {v}" for k, v in headers.items()]).lower()
    predicted = []
    versions = []
    scores: dict[str, float] = {}
    for product, needles in signatures.items():
        hits = sum(1 for needle in needles if needle in corpus)
        score = hits / len(needles)
        if score >= threshold:
            predicted.append(product)
            scores[product] = score
            version = _extract_product_version(corpus, product)
            if version:
                versions.append({"product": product, "version": version})
    return {"predicted_products": sorted(predicted), "predicted_versions": versions, "confidence_scores": scores, "model_profile": "deterministic-local-signature-catalog"}


def _extract_product_version(corpus: str, product: str) -> str | None:
    marker = product.lower() + "/"
    if marker not in corpus:
        return None
    suffix = corpus.split(marker, 1)[1]
    token = suffix.split()[0].strip(";,)")
    return token or None


def _nmap_profile_args(scan_profile: str, timing_profile: str) -> list[str]:
    args: list[str] = []
    if scan_profile == "quick":
        args.append("--top-ports")
        args.append("100")
    elif scan_profile == "deep":
        args.extend(["-sV", "--version-light"])
    if timing_profile == "low_noise":
        args.append("-T2")
    elif timing_profile == "normal":
        args.append("-T3")
    elif timing_profile == "fast":
        args.append("-T4")
    return args


def _masscan_rate(rate_profile: str) -> int:
    return {"low": 100, "normal": 1000, "fast": 5000, "custom": 100}.get(rate_profile, 100)


def _parse_nmap_xml_ports(stdout: str) -> list[dict[str, Any]]:
    import xml.etree.ElementTree as ET

    if not stdout.strip():
        return []
    root = ET.fromstring(stdout)
    parsed_ports: list[dict[str, Any]] = []
    for host in root.findall("host"):
        address = ""
        address_node = host.find("address")
        if address_node is not None:
            address = str(address_node.attrib.get("addr", ""))
        for port_node in host.findall("./ports/port"):
            state = port_node.find("state")
            if state is None or state.attrib.get("state") != "open":
                continue
            service = port_node.find("service")
            parsed_ports.append(
                {
                    "host": address,
                    "port": int(port_node.attrib["portid"]),
                    "transport": port_node.attrib.get("protocol", "tcp"),
                    "service_name": service.attrib.get("name", "unknown") if service is not None else "unknown",
                    "product": service.attrib.get("product") if service is not None else None,
                    "version": service.attrib.get("version") if service is not None else None,
                }
            )
    return parsed_ports


def _parse_masscan_json_ports(stdout: str) -> list[dict[str, Any]]:
    stripped = stdout.strip().rstrip(",")
    if not stripped:
        return []
    payload: Any
    if stripped.startswith("["):
        payload = json.loads(stripped)
    else:
        payload = _json_lines(stripped)
    services: list[dict[str, Any]] = []
    for item in payload if isinstance(payload, list) else []:
        if not isinstance(item, dict):
            continue
        host = str(item.get("ip", ""))
        for port_item in item.get("ports", []) if isinstance(item.get("ports"), list) else []:
            if not isinstance(port_item, dict):
                continue
            services.append(
                {
                    "host": host,
                    "port": int(port_item.get("port")),
                    "transport": str(port_item.get("proto", "tcp")),
                    "service_name": "unknown",
                }
            )
    return services


def _parse_naabu_json_services(stdout: str, target: str) -> list[dict[str, Any]]:
    services: list[dict[str, Any]] = []
    for item in _json_lines(stdout):
        host = str(item.get("host") or item.get("ip") or target)
        port = item.get("port")
        if port is None:
            continue
        services.append(
            {
                "host": host,
                "port": int(port),
                "transport": "tcp",
                "service_name": "http" if int(port) == 80 else "https" if int(port) == 443 else "unknown",
            }
        )
    if services:
        return services
    for line in _text_lines(stdout):
        if ":" not in line:
            continue
        host, port_text = line.rsplit(":", 1)
        if port_text.isdigit():
            port = int(port_text)
            services.append({"host": host, "port": port, "transport": "tcp", "service_name": "unknown"})
    return services


def _urls_from_services(services: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []
    for service in services:
        host = str(service.get("host", "")).strip()
        port = int(service.get("port", 0))
        if not host or port <= 0:
            continue
        scheme = "https" if port in {443, 8443} else "http"
        suffix = "" if port in {80, 443} else f":{port}"
        urls.append(f"{scheme}://{host}{suffix}")
    return sorted(set(urls))


def _parse_httpx_json_services(stdout: str) -> list[dict[str, Any]]:
    services: list[dict[str, Any]] = []
    for item in _json_lines(stdout):
        url = str(item.get("url") or item.get("input") or "")
        if not url:
            continue
        services.append(
            {
                "url": url,
                "status_code": item.get("status_code"),
                "title": item.get("title"),
                "webserver": item.get("webserver"),
                "technologies": item.get("tech") if isinstance(item.get("tech"), list) else [],
                "content_length": item.get("content_length"),
            }
        )
    return services


def _parse_katana_urls(stdout: str) -> list[str]:
    urls: list[str] = []
    for item in _json_lines(stdout):
        url = str(item.get("request", {}).get("endpoint") if isinstance(item.get("request"), dict) else item.get("url") or "")
        if url.startswith(("http://", "https://")):
            urls.append(url)
    for line in _text_lines(stdout):
        if line.startswith(("http://", "https://")):
            urls.append(line)
    return sorted(set(urls))


def _technology_hints(web_services: list[dict[str, Any]]) -> list[str]:
    hints: set[str] = set()
    for service in web_services:
        for value in service.get("technologies", []) if isinstance(service.get("technologies"), list) else []:
            hints.add(str(value))
        if service.get("webserver"):
            hints.add(str(service["webserver"]))
    return sorted(hints)


def _port_graph_updates(target: str, ports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "ServiceFingerprint",
            "host": item.get("host") or target,
            "port": item.get("port"),
            "transport": item.get("transport", "tcp"),
            "service_name": item.get("service_name", "unknown"),
        }
        for item in ports
    ]


def _web_graph_updates(target: str, web_services: list[dict[str, Any]], crawled_urls: list[str]) -> list[dict[str, Any]]:
    updates: list[dict[str, Any]] = []
    for service in web_services:
        updates.append({"type": "WebEndpointNode", "target": target, "url": service.get("url"), "status_code": service.get("status_code")})
        for technology in service.get("technologies", []) if isinstance(service.get("technologies"), list) else []:
            updates.append({"type": "TechnologyNode", "target": target, "technology": str(technology)})
    for url in crawled_urls:
        updates.append({"type": "WebEndpointNode", "target": target, "url": url, "source": "katana"})
    return updates


def _parse_subfinder_domains(stdout: str, domain: str) -> list[str]:
    subdomains: set[str] = set()
    for item in _json_lines(stdout):
        host = str(item.get("host") or item.get("subdomain") or item.get("value") or "").strip().lower().rstrip(".")
        if host == domain or host.endswith(f".{domain}"):
            subdomains.add(host)
    for line in _text_lines(stdout):
        host = line.strip().lower().rstrip(".")
        if host == domain or host.endswith(f".{domain}"):
            subdomains.add(host)
    return sorted(subdomains)


def _parse_amass_json(stdout: str, domain: str) -> dict[str, Any]:
    subdomains: set[str] = set()
    ips: set[str] = set()
    asn_records: list[dict[str, Any]] = []
    graph_edges: list[dict[str, Any]] = []
    for item in _json_lines(stdout):
        name = str(item.get("name") or item.get("domain") or "").strip().lower().rstrip(".")
        if name == domain or name.endswith(f".{domain}"):
            subdomains.add(name)
        for address in item.get("addresses", []) if isinstance(item.get("addresses"), list) else []:
            if not isinstance(address, dict):
                continue
            ip_value = str(address.get("ip", "")).strip()
            if ip_value:
                ips.add(ip_value)
                graph_edges.append({"source": name or domain, "target": ip_value, "relationship": "RESOLVES_TO"})
            asn = address.get("asn")
            if asn:
                asn_records.append({"asn": asn, "desc": address.get("desc"), "cidr": address.get("cidr")})
    return {
        "subdomains": sorted(subdomains),
        "ips": sorted(ips),
        "asn_records": asn_records,
        "graph_edges": graph_edges,
    }


def _collect_file_hashes(root: Path, suffixes: set[str]) -> list[dict[str, Any]]:
    if not root.is_dir():
        return []
    artifacts: list[dict[str, Any]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file() and item.suffix.lower() in suffixes):
        content = path.read_bytes()
        artifacts.append({"path": path.as_posix(), "sha256": hashlib.sha256(content).hexdigest(), "size_bytes": len(content)})
    return artifacts


def _domain_graph_updates(domain: str, subdomains: list[str]) -> list[dict[str, Any]]:
    return [{"type": "HostNode", "domain": domain, "host": subdomain} for subdomain in subdomains]


def _normalize_shodan_host(payload: dict[str, Any], include_banners: bool) -> dict[str, Any]:
    services = payload.get("data", [])
    passive_ports: list[dict[str, Any]] = []
    banners: list[dict[str, Any]] = []
    for item in services if isinstance(services, list) else []:
        if not isinstance(item, dict):
            continue
        passive_ports.append(
            {
                "ip": payload.get("ip_str") or item.get("ip_str"),
                "port": item.get("port"),
                "transport": item.get("transport", "tcp"),
                "product": item.get("product"),
                "version": item.get("version"),
            }
        )
        if include_banners and item.get("data"):
            banners.append({"port": item.get("port"), "data": str(item.get("data"))[:2000]})
    return {
        "passive_ports": passive_ports,
        "passive_service_inventory": _canonical_passive_services(passive_ports, "shodan"),
        "banners": banners,
        "host_metadata": {"ip": payload.get("ip_str"), "hostnames": payload.get("hostnames", []), "org": payload.get("org")},
        "attack_surface_updates": _port_graph_updates(str(payload.get("ip_str", "")), passive_ports),
    }


def _normalize_shodan_search(payload: dict[str, Any], include_banners: bool) -> dict[str, Any]:
    matches = payload.get("matches", [])
    synthetic_host = {"data": matches}
    normalized = _normalize_shodan_host(synthetic_host, include_banners)
    normalized["host_metadata"] = {"total": payload.get("total"), "query_result": True}
    return normalized


def _normalize_censys(payload: dict[str, Any], target_type: str) -> dict[str, Any]:
    result = payload.get("result", payload)
    hits = result.get("hits", []) if isinstance(result, dict) else []
    passive_services: list[dict[str, Any]] = []
    certificates: list[dict[str, Any]] = []
    for hit in hits if isinstance(hits, list) else []:
        if not isinstance(hit, dict):
            continue
        if target_type == "certificate":
            certificates.append({"fingerprint_sha256": hit.get("fingerprint_sha256"), "names": hit.get("names", [])})
            continue
        services = hit.get("services", [])
        for service in services if isinstance(services, list) else []:
            if isinstance(service, dict):
                passive_services.append({"ip": hit.get("ip"), "port": service.get("port"), "service_name": service.get("service_name"), "transport": service.get("transport_protocol", "tcp")})
    return {
        "certificates": certificates,
        "passive_services": passive_services,
        "passive_service_inventory": _canonical_passive_services(passive_services, "censys"),
        "host_metadata": {"total": result.get("total") if isinstance(result, dict) else None},
        "attack_surface_updates": _port_graph_updates("", passive_services),
    }


def _canonical_passive_services(records: list[dict[str, Any]], provider: str) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    seen: set[tuple[str, int | None, str]] = set()
    for record in records:
        raw_port = record.get("port")
        try:
            port = int(raw_port) if raw_port is not None else None
        except (TypeError, ValueError):
            port = None
        transport = str(record.get("transport") or record.get("transport_protocol") or "tcp").lower()
        item = {
            "ip": str(record.get("ip") or ""),
            "port": port,
            "transport": transport,
            "service_name": record.get("service_name") or record.get("product"),
            "product": record.get("product"),
            "version": record.get("version"),
            "source_provider": provider,
        }
        key = (item["ip"], item["port"], item["transport"])
        if key not in seen:
            seen.add(key)
            inventory.append(item)
    return inventory


def _normalize_otx(payload: dict[str, Any]) -> dict[str, Any]:
    pulses = payload.get("pulse_info", {}).get("pulses", []) if isinstance(payload.get("pulse_info"), dict) else []
    related = payload.get("related", {})
    related_indicators: list[dict[str, Any]] = []
    if isinstance(related, dict):
        for key, value in related.items():
            if isinstance(value, list):
                related_indicators.extend({"type": key, "indicator": str(item)} for item in value[:50])
    return {
        "iocs": payload.get("validation", []) if isinstance(payload.get("validation"), list) else [],
        "related_indicators": related_indicators,
        "pulses": [{"id": pulse.get("id"), "name": pulse.get("name")} for pulse in pulses if isinstance(pulse, dict)],
    }


def _normalize_securitytrails_subdomains(payload: dict[str, Any], domain: str) -> list[str]:
    raw_subdomains = payload.get("subdomains", [])
    return sorted({f"{str(item).strip().lower()}.{domain}" for item in raw_subdomains if str(item).strip()})


def _normalize_securitytrails_dns_history(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in payload.get("records", []) if isinstance(payload.get("records"), list) else []:
        if not isinstance(item, dict):
            continue
        values = item.get("values", [])
        records.append(
            {
                "first_seen": item.get("first_seen"),
                "last_seen": item.get("last_seen"),
                "values": values if isinstance(values, list) else [],
            }
        )
    return records


def _email_arg(value: str) -> str:
    email = value.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@") or "." not in email.rsplit("@", 1)[1]:
        raise ContractError("email must be a valid email address.")
    return email


def _redact_email(email: str) -> str:
    local, domain = email.split("@", 1)
    return f"{local[:1]}***@{domain}"


def _json_or_empty_list(response: requests.Response) -> list[Any]:
    if response.status_code == 404:
        return []
    try:
        payload = response.json()
    except ValueError as error:
        raise ContractError("API response was not valid JSON.") from error
    if not isinstance(payload, list):
        raise ContractError("API response must be a JSON list.")
    return payload


def _json_object_response(response: requests.Response, source_name: str) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as error:
        raise ContractError(f"{source_name} API response was not valid JSON.") from error
    if not isinstance(payload, dict):
        raise ContractError(f"{source_name} API response must be a JSON object.")
    return payload


def _normalize_hibp_breaches(items: list[Any]) -> list[str]:
    return sorted({str(item.get("Name") or item.get("Title")) for item in items if isinstance(item, dict) and (item.get("Name") or item.get("Title"))})


def _normalize_hibp_pastes(items: list[Any]) -> list[dict[str, Any]]:
    return [
        {"source": item.get("Source"), "id": item.get("Id"), "date": item.get("Date"), "title": item.get("Title")}
        for item in items
        if isinstance(item, dict)
    ]


def _normalize_dehashed(payload: dict[str, Any], redact: bool) -> list[dict[str, Any]]:
    entries = payload.get("entries", payload.get("results", []))
    records: list[dict[str, Any]] = []
    for item in entries if isinstance(entries, list) else []:
        if not isinstance(item, dict):
            continue
        email_value = str(item.get("email", ""))
        records.append(
            {
                "email": _redact_email(email_value) if redact and "@" in email_value else email_value,
                "username": item.get("username"),
                "domain": item.get("domain"),
                "database_name": item.get("database_name") or item.get("source"),
                "has_password": bool(item.get("password") or item.get("hashed_password")),
            }
        )
    return records


def _normalize_intelx(payload: dict[str, Any], query_type: str, source_url: str) -> dict[str, Any]:
    records = payload.get("records", payload.get("selectors", []))
    intel_records = [
        {"name": item.get("name") or item.get("selectorvalue"), "bucket": item.get("bucket"), "date": item.get("date"), "xref": item.get("xref")}
        for item in records
        if isinstance(item, dict)
    ]
    source_references = sorted({str(item.get("xref")) for item in records if isinstance(item, dict) and item.get("xref")})
    if not source_references:
        source_references = [source_url]
    return {"query_type": query_type, "intel_records": intel_records, "source_references": source_references, "source_urls": [source_url]}


def _normalize_spiderfoot_api(payload: dict[str, Any], source_url: str) -> dict[str, Any]:
    entities = payload.get("entities", payload.get("data", []))
    return {
        "osint_graph": {"source": "spiderfoot_api", "source_url": source_url},
        "discovered_entities": entities if isinstance(entities, list) else [],
        "relationship_edges": payload.get("edges", []) if isinstance(payload.get("edges", []), list) else [],
        "report_path": None,
    }


def _normalize_spiderfoot_cli(stdout: str, command: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {"raw_lines": _text_lines(stdout)}
    if not isinstance(payload, dict):
        payload = {"items": payload}
    return {
        "osint_graph": {"source": "spiderfoot_cli", "command": command},
        "discovered_entities": payload.get("data", payload.get("items", [])) if isinstance(payload.get("data", payload.get("items", [])), list) else [],
        "relationship_edges": payload.get("edges", []) if isinstance(payload.get("edges", []), list) else [],
        "report_path": payload.get("report_path"),
    }


def _normalize_theharvester(stdout: str, domain: str, command: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(stdout) if stdout.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    emails = sorted({str(item).lower() for item in payload.get("emails", []) if isinstance(item, str)})
    hosts = sorted({str(item).lower() for item in payload.get("hosts", []) if isinstance(item, str)})
    if not emails:
        emails = sorted({line for line in _text_lines(stdout) if "@" in line and domain in line})
    if not hosts:
        hosts = sorted({line.lower().rstrip(".") for line in _text_lines(stdout) if line.lower().endswith(f".{domain}")})
    return {"emails": emails, "hosts": hosts, "subdomains": hosts, "source_references": payload.get("sources", []), "command": command}


def _normalize_holehe(stdout: str, email: str) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for line in _text_lines(stdout):
        if "[+]" in line or "exists" in line.lower():
            matches.append({"site": line.replace("[+]", "").strip(), "status": "exists_or_likely"})
    return {"email": _redact_email(email), "account_presence_findings": matches, "site_matches": [match["site"] for match in matches]}


def _safe_identifier(value: str, field_name: str) -> str:
    identifier = value.strip()
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-")
    if not identifier or any(char not in allowed for char in identifier):
        raise ContractError(f"{field_name} contains unsupported characters.")
    return identifier


def _normalize_profile_lines(stdout: str, username: str) -> dict[str, Any]:
    parsed: dict[str, dict[str, str]] = {}
    for line in _text_lines(stdout):
        parts = line.split()
        if not parts or not parts[-1].startswith(("http://", "https://")):
            continue
        url = parts[-1]
        site_text = line.rsplit(url, 1)[0].replace("[+]", "").replace(":", " ").strip()
        site = site_text.split()[0] if site_text.split() else "unknown"
        parsed[url] = {"username": username, "url": url, "site": site, "source": "profile_lookup"}
    urls = sorted(parsed)
    profiles = [parsed[url] for url in urls]
    return {"social_profiles": profiles, "profile_urls": urls, "report_path": None}


def _normalize_ghunt(stdout: str, identifier: str) -> dict[str, Any]:
    lines = _text_lines(stdout)
    return {
        "google_profile_findings": [{"line": line} for line in lines[:50]],
        "public_identifiers": [identifier],
        "report_path": None,
    }


def _existing_files(parameters: dict[str, Any], name: str) -> list[Path]:
    paths = [Path(value) for value in _string_list(parameters, name)]
    if not paths:
        raise ContractError(f"{name} must include at least one file path.")
    missing = [path.as_posix() for path in paths if not path.is_file()]
    if missing:
        raise ContractError(f"{name} contains missing files: {', '.join(missing)}.")
    return paths


def _normalize_metadata_json_or_text(stdout: str, redact: bool) -> dict[str, Any]:
    try:
        payload: Any = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        payload = [{"RawLine": line} for line in _text_lines(stdout)]
    findings = payload if isinstance(payload, list) else [payload] if isinstance(payload, dict) else []
    return _metadata_summary(findings, redact)


def _normalize_exiftool(stdout: str, redact: bool) -> dict[str, Any]:
    return _normalize_metadata_json_or_text(stdout, redact)


def _metadata_summary(findings: list[Any], redact: bool) -> dict[str, Any]:
    metadata_findings = [item for item in findings if isinstance(item, dict)]
    authors = sorted({str(item.get("Author") or item.get("Creator") or item.get("LastModifiedBy")) for item in metadata_findings if item.get("Author") or item.get("Creator") or item.get("LastModifiedBy")})
    software_versions = sorted({str(item.get("Software") or item.get("Producer") or item.get("CreatorTool")) for item in metadata_findings if item.get("Software") or item.get("Producer") or item.get("CreatorTool")})
    paths = sorted({str(item.get("SourceFile") or item.get("FileName")) for item in metadata_findings if item.get("SourceFile") or item.get("FileName")})
    gps_metadata = [item for item in metadata_findings if any(str(key).startswith("GPS") for key in item)]
    if redact:
        paths = [Path(path).name for path in paths]
    return {
        "metadata_findings": metadata_findings,
        "authors": authors,
        "software_versions": software_versions,
        "paths": paths,
        "gps_metadata": gps_metadata,
        "device_metadata": [item for item in metadata_findings if item.get("Model") or item.get("Make")],
        "software_metadata": software_versions,
    }


def _dork_query(target: str, profile: str) -> str:
    templates = {
        "documents": 'site:{target} (filetype:pdf OR filetype:doc OR filetype:xls)',
        "backups": 'site:{target} (ext:bak OR ext:old OR ext:backup)',
        "panels": 'site:{target} (intitle:login OR inurl:admin)',
        "configs": 'site:{target} (ext:env OR ext:conf OR ext:config)',
        "custom": target,
    }
    return templates[profile].format(target=target)


def _normalize_search_results(payload: dict[str, Any], source_url: str) -> dict[str, Any]:
    items = payload.get("items", payload.get("organic_results", []))
    results = [
        {"title": item.get("title"), "url": item.get("link") or item.get("url"), "snippet": item.get("snippet")}
        for item in items
        if isinstance(item, dict)
    ]
    urls = [str(item["url"]) for item in results if item.get("url")]
    return {
        "search_results": results,
        "exposed_documents": [url for url in urls if any(url.lower().endswith(ext) for ext in (".pdf", ".doc", ".docx", ".xls", ".xlsx"))],
        "exposed_paths": urls,
        "source_urls": [source_url],
    }


def _normalize_ripe_stat(payload: dict[str, Any], lookup_type: str, source_url: str) -> dict[str, Any]:
    data = payload.get("data", payload)
    asns = data.get("asns", []) if isinstance(data, dict) else []
    prefixes = data.get("prefixes", []) if isinstance(data, dict) else []
    return {
        "lookup_type": lookup_type,
        "asn_records": asns if isinstance(asns, list) else [],
        "bgp_prefixes": prefixes if isinstance(prefixes, list) else [],
        "geolocation": {"source": "ripe_stat", "resource": data.get("resource") if isinstance(data, dict) else None},
        "source_urls": [source_url],
    }


def _normalize_whois_history(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("records", payload.get("WhoisRecord", []))
    if isinstance(records, dict):
        records = [records]
    return [item for item in records if isinstance(item, dict)]


def _normalize_rdap_whois(payload: dict[str, Any], historical_ownership: list[dict[str, Any]], source_urls: list[str]) -> dict[str, Any]:
    registrar_history = []
    for entity in payload.get("entities", []) if isinstance(payload.get("entities", []), list) else []:
        if isinstance(entity, dict):
            registrar_history.append({"roles": entity.get("roles", []), "handle": entity.get("handle")})
    return {
        "whois_records": payload,
        "historical_ownership": historical_ownership,
        "registrar_history": registrar_history,
        "source_urls": source_urls,
    }


def _reverse_dns_records(value: str, limit: int) -> list[dict[str, Any]]:
    try:
        network = ip_network(value, strict=False)
        ips = [str(ip) for index, ip in enumerate(network.hosts()) if index < limit]
    except ValueError:
        try:
            ips = [str(ip_address(value))]
        except ValueError as error:
            raise ContractError("ip_or_range must be an IP address or CIDR range.") from error
    records: list[dict[str, Any]] = []
    for ip_value in ips:
        try:
            primary, aliases, _ = socket.gethostbyaddr(ip_value)
            domains = sorted({primary, *aliases})
            status = "RESOLVED"
        except (socket.herror, socket.gaierror) as error:
            domains = []
            status = "NOT_FOUND"
            records.append({"ip": ip_value, "domains": domains, "status": status, "error": str(error)})
            continue
        records.append({"ip": ip_value, "domains": domains, "status": status, "error": None})
    return records
