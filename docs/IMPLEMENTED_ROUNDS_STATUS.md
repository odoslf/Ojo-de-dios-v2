# Implemented roadmap rounds status

This document records the real state of the modules and platform surfaces implemented through rounds 2-28. It is intentionally conservative: a module is only listed as implemented when it has concrete code, registry-visible techniques or runtime checks, and contract tests. Catalog `readiness` fields remain authoritative product lifecycle metadata; the per-module `implementation_status` blocks in manifests record implementation progress without pretending that unimplemented techniques are complete.

## Current implemented surfaces

| Area | Real implementation | Tests / verification | Explicit limits |
| --- | --- | --- | --- |
| M01 OSINT | 47 registered `READY_CONTROLLED` OSINT techniques in `app.modules.m01_osint.techniques`, including surface discovery, passive APIs, metadata/DNS, social/code OSINT, internal read-only discovery and AI-assisted scraping planners. | `tests/test_m01_surface_discovery_techniques.py`, `tests/test_m01_roadmap_verification_contract.py`. | Active discovery still requires operator confirmation/scope; external tools/APIs may return missing-tool/config errors instead of fake success. |
| M03 Network Services | 3 registered passive/read-only fingerprinting techniques for service maps, Nmap XML imports and banner fingerprints. | `tests/test_m03_passive_fingerprinting_contract.py`. | No exploitation, authentication attacks, payload delivery or service mutation. |
| M09 Scraping Intelligence | 7 base scraping infrastructure techniques plus 2 local-AI techniques for JSON-only plans/table analysis. | `tests/test_m09_scraping_base_contract.py`, `tests/test_m09_ai_integration_contract.py`. | No CAPTCHA bypass automation, proxy abuse or uncontrolled scraping; AI responses are validated and non-executing. |
| M12 Orchestration | 1 registered orchestration planning technique and concrete helpers to build/run constrained plans through existing registry/JobRunner primitives. | `tests/test_m12_orchestration_contract.py`. | Only coordinates allowed modules; it does not add attack/exploit logic. |
| M15 Cloud | 4 registered read-only audits for inventory, IAM, Kubernetes RBAC and container scanner reports. | `tests/test_m15_cloud_readonly_contract.py`. | No cloud mutations, metadata endpoint probing, secret extraction or deployment. |
| M16 Ops Quality | Runtime/readiness checks for evidence quality, version-lock readiness, runtime cleanup plan, export preparation and Angel/Hermes status handling. | `tests/test_m16_readiness_contract.py`. | Does not call external services or delete runtime files during checks. |
| M18 Honeypots/Deception | 3 registered defensive techniques for honeypot bundle preparation, IOC extraction and passive intrusion profiling. | `tests/test_m18_honeypots_deception_contract.py`. | Defensive only; it does not launch services, counterattack or beacon. |
| LaIA chat | Local chat API/UI with prompt bounding, message validation, secret redaction and optional uploaded-document RAG context. | `tests/test_laia_chat_api_contract.py`, `tests/test_laia_chat_frontend_contract.py`. | Does not execute modules and does not call external AI. |
| RAG | Local upload ingestion, deterministic chunking, hashed embeddings, semantic search, context packs and round-trip verification. | `tests/test_rag_document_pipeline_contract.py`. | UTF-8 text formats only at this stage; no model download, training or external network calls. |
| Dashboard | `/modules` and module detail pages show real implementation counts from registry/docs/tools/workspace instead of manifest-only placeholders. | `tests/test_module_dashboard_status_contract.py`, `tests/test_targets_pages_templates_exist.py`. | Display only; no implicit execution. |

## Manifest policy

The worked module manifests now include an `implementation_status` object with these fields:

- `source`: how the status is derived (`registry_and_contract_tests`);
- `readiness_status`: dashboard/runtime implementation state;
- `documented_technique_count`;
- `implemented_technique_count`;
- `ready_technique_count`;
- `local_ai_technique_count`;
- `implementation_statuses`;
- `scope_note`.

The top-level `readiness` field remains unchanged because it is validated against the module catalog and represents product lifecycle metadata, not the live implementation count.

## Coverage note for round 28

The broad non-TestClient suite currently passes in this environment. Full `pytest -q` collection is blocked here because `httpx` is missing for FastAPI/Starlette `TestClient`; `requirements-dev.txt` already declares `httpx==0.28.1`, but installing it through the configured package index failed with HTTP 403 in this container.
