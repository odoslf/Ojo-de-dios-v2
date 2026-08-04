"""Authoritative module catalog for Ojo de Dios.

The catalog describes the product-level module structure. It is intentionally
separate from the technique registry: modules 1-16 are the currently documented
official product modules, while 17-20 are named reserved slots. They are not a
final architectural limit: ModuleRegistry, TechniqueRegistry, PanelRegistry and
WorkerRegistry must remain open-ended and must not hardcode a maximum module
number. Reserved modules are discoverable for planning, but they are not treated
as implemented capabilities.
"""

from dataclasses import dataclass
from typing import Literal

ModuleLifecycle = Literal["official", "reserved"]
ModuleReadiness = Literal["documented", "reserved_future_module"]

MODULE_STATUS_DOCUMENTED: ModuleReadiness = "documented"
MODULE_STATUS_RESERVED_FUTURE: ModuleReadiness = "reserved_future_module"

MODULE_LIFECYCLE_OFFICIAL: ModuleLifecycle = "official"
MODULE_LIFECYCLE_RESERVED: ModuleLifecycle = "reserved"

OFFICIAL_MODULE_COUNT = 16
RESERVED_MODULE_COUNT = 4
TOTAL_MODULE_SLOTS = OFFICIAL_MODULE_COUNT + RESERVED_MODULE_COUNT


@dataclass(frozen=True, slots=True)
class ModuleCatalogEntry:
    """Immutable product module descriptor.

    The descriptor is metadata only: it does not imply executable techniques,
    available tools, or operational readiness. Execution readiness is derived
    later from ToolHealth, VersionLock, permissions, workers, scope, and
    EvidenceStore state.
    """

    module_number: int
    module_id: str
    slug: str
    display_name: str
    description: str
    lifecycle: ModuleLifecycle
    readiness: ModuleReadiness
    doc_path: str | None
    official: bool
    reserved: bool
    requires_user_definition: bool
    notes: tuple[str, ...] = ()

    @property
    def package_path(self) -> str:
        """Return the repository-relative Python package path for this module."""
        return f"app/modules/{self.module_id}"

    @property
    def manifest_path(self) -> str:
        """Return the repository-relative manifest path for this module."""
        return f"{self.package_path}/module_manifest.json"

    @property
    def workspace_path(self) -> str:
        """Return the repository-relative workspace root for this module."""
        return f"storage/workspaces/{self.module_id}"

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation of the module descriptor."""
        return {
            "module_number": self.module_number,
            "module_id": self.module_id,
            "slug": self.slug,
            "display_name": self.display_name,
            "description": self.description,
            "lifecycle": self.lifecycle,
            "readiness": self.readiness,
            "doc_path": self.doc_path,
            "official": self.official,
            "reserved": self.reserved,
            "requires_user_definition": self.requires_user_definition,
            "notes": list(self.notes),
            "package_path": self.package_path,
            "manifest_path": self.manifest_path,
            "workspace_path": self.workspace_path,
        }


_OFFICIAL_MODULES: tuple[ModuleCatalogEntry, ...] = (
    ModuleCatalogEntry(
        1,
        "m01_osint",
        "osint",
        "OSINT",
        "Open-source intelligence intake for domains, IPs, ranges, emails, people and companies.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/01_OSINT.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        2,
        "m02_vulnerabilities",
        "vulnerabilities",
        "Vulnerabilidades",
        "Service, technology and version analysis that produces CVE candidates and risk context.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/02_VULNERABILITIES.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        3,
        "m03_network_services",
        "network-services",
        "Explotación servicios de red",
        "Network service fingerprinting and mapping to registered techniques.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/03_NETWORK_EXPLOITATION.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        4,
        "m04_web_intrusion",
        "web-intrusion",
        "Intrusión web avanzada",
        "Web assessment workspace for URLs, headers, cookies, auth context and approved scope.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/04_WEB_INTRUSION.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        5,
        "m05_credentials",
        "credentials",
        "Credenciales y Autenticación",
        "Credential findings, sources, dictionaries, hashes, tickets, redaction and evidence handoff.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/05_CREDENTIALS.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        6,
        "m06_mitm_network",
        "mitm-network",
        "MITM / Red",
        "Network, interface, PCAP, tunnel and integrated DNS evidence workflows.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/06_MITM_NETWORK.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        7,
        "m07_post_exploitation",
        "post-exploitation",
        "Post-explotación y Movimiento Lateral",
        "Session, route and evidence views with sensitive logic kept behind user implementation.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/07_POST_EXPLOITATION.md",
        True,
        False,
        False,
        ("Sensitive operational logic remains user-provided when required.",),
    ),
    ModuleCatalogEntry(
        8,
        "m08_dos_resilience",
        "dos-resilience",
        "DoS / Resiliencia",
        "Resilience metrics, limits, stop controls and evidence for authorized resilience testing.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/08_DOS_RESILIENCE.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        9,
        "m09_scraping_intelligence",
        "scraping-intelligence",
        "Scraping Inteligente X4 + X5 + IA",
        "X4 connector, X5 scraping planner, normalization and export workflows.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/09_SCRAPING_INTELLIGENCE.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        10,
        "m10_wireless_rf",
        "wireless-rf",
        "Wireless / RF general",
        "Wireless and RF general workflows for WiFi, BLE, RFID/NFC, Zigbee, Z-Wave and radio evidence surfaces.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/10_WIFI_BLUETOOTH.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        11,
        "m11_iot_physical",
        "iot-physical",
        "IoT / físicos",
        "Device, camera, printer, domotics and physical-device evidence workflows.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/11_IOT_PHYSICAL.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        12,
        "m12_orchestration",
        "orchestration",
        "Orquestación X5 + IA + Hermes Agent Lab",
        "X5, LaIA/Mistral, Hermes Agent, DeepSeek-assisted planning and controlled promotion.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/12_ORCHESTRATION_X5_AI_HERMES.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        13,
        "m13_android",
        "android",
        "Android",
        "Android assessment workflows, tool contracts, evidence, handoffs and safe closure.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/13_ANDROID.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        14,
        "m14_phishing",
        "phishing",
        "Campañas de Simulación y Concienciación",
        "Authorized campaign, template, evidence and reporting workflows.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/14_PHISHING.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        15,
        "m15_cloud",
        "cloud",
        "Cloud / Containers / Kubernetes",
        "Cloud, container and Kubernetes workflows that distinguish read-only from mutation modes.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/15_CLOUD.md",
        True,
        False,
        False,
    ),
    ModuleCatalogEntry(
        16,
        "m16_ops_quality",
        "ops-quality",
        "Excelencia operativa / Evidence / Calidad / Mantenimiento",
        "Health, readiness, version lock, evidence quality, runtime cleanup and external export preparation.",
        MODULE_LIFECYCLE_OFFICIAL,
        MODULE_STATUS_DOCUMENTED,
        "docs/techniques/16_EVIDENCE_OPS.md",
        True,
        False,
        False,
    ),
)

_RESERVED_MODULES: tuple[ModuleCatalogEntry, ...] = (
    ModuleCatalogEntry(
        17,
        "m17_hackrf_sdr",
        "hackrf-sdr",
        "Laboratorio de Radiofrecuencia (HackRF One)",
        "Reserved laboratory for authorized RF security testing with HackRF One, spectrum analysis, Sub-GHz signals, TETRA/TETRAPOL, GSM/LTE, GPS, Bluetooth audio and special signals.",
        MODULE_LIFECYCLE_RESERVED,
        MODULE_STATUS_RESERVED_FUTURE,
        None,
        False,
        True,
        True,
        ("Reserved module: SDR capability owner; other modules may expose mirrored actions through capability_ref.", "Una capacidad real, múltiples superficies de uso."),
    ),
    ModuleCatalogEntry(
        18,
        "m18_honeypots_deception",
        "honeypots-deception",
        "Sistema de Señuelos y Análisis de Intrusiones",
        "Reserved laboratory for honeypots, deception, passive intrusion profiling, indicators of compromise and approved response workflows.",
        MODULE_LIFECYCLE_RESERVED,
        MODULE_STATUS_RESERVED_FUTURE,
        None,
        False,
        True,
        True,
        ("Reserved module: definition provided by operator; no executable techniques, tools or workers are implied yet.",),
    ),
    ModuleCatalogEntry(
        19,
        "m19_integrations_agents",
        "integrations-agents",
        "Auditoría de Seguridad en Sistemas de IA",
        "Reserved laboratory for AI security assessment across infrastructure, models and AI-enabled applications.",
        MODULE_LIFECYCLE_RESERVED,
        MODULE_STATUS_RESERVED_FUTURE,
        None,
        False,
        True,
        True,
        ("Reserved module: definition provided by operator; no executable techniques, tools or workers are implied yet.",),
    ),
    ModuleCatalogEntry(
        20,
        "m20_future_expansion",
        "future-expansion",
        "Laboratorio de Análisis de Vulnerabilidades",
        "Reserved laboratory for advanced vulnerability analysis in binaries, network services, web applications, smart contracts and mobile or desktop applications.",
        MODULE_LIFECYCLE_RESERVED,
        MODULE_STATUS_RESERVED_FUTURE,
        None,
        False,
        True,
        True,
        ("Reserved module: definition provided by operator; no executable techniques, tools or workers are implied yet.",),
    ),
)

MODULE_CATALOG: tuple[ModuleCatalogEntry, ...] = _OFFICIAL_MODULES + _RESERVED_MODULES


def list_modules(include_reserved: bool = True) -> tuple[ModuleCatalogEntry, ...]:
    """Return module catalog entries sorted by module number."""
    if include_reserved:
        return MODULE_CATALOG
    return tuple(module for module in MODULE_CATALOG if not module.reserved)


def list_official_modules() -> tuple[ModuleCatalogEntry, ...]:
    """Return official documented modules only."""
    return tuple(module for module in MODULE_CATALOG if module.official)


def list_reserved_modules() -> tuple[ModuleCatalogEntry, ...]:
    """Return reserved future module slots only."""
    return tuple(module for module in MODULE_CATALOG if module.reserved)


def get_module_by_number(module_number: int) -> ModuleCatalogEntry | None:
    """Return a module by numeric slot, if present."""
    return next((module for module in MODULE_CATALOG if module.module_number == module_number), None)


def get_module_by_id(module_id: str) -> ModuleCatalogEntry | None:
    """Return a module by stable module id, if present."""
    return next((module for module in MODULE_CATALOG if module.module_id == module_id), None)


def require_module_by_number(module_number: int) -> ModuleCatalogEntry:
    """Return a module by number or raise ValueError."""
    module = get_module_by_number(module_number)
    if module is None:
        raise ValueError(f"Unknown module number: {module_number}.")
    return module


def require_module_by_id(module_id: str) -> ModuleCatalogEntry:
    """Return a module by id or raise ValueError."""
    module = get_module_by_id(module_id)
    if module is None:
        raise ValueError(f"Unknown module id: {module_id}.")
    return module


def module_catalog_as_dicts(include_reserved: bool = True) -> list[dict[str, object]]:
    """Return JSON-ready catalog entries."""
    return [module.to_dict() for module in list_modules(include_reserved=include_reserved)]
