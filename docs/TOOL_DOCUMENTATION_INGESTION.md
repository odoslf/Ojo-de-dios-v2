# TOOL DOCUMENTATION INGESTION — OJO DE DIOS

## Objetivo

LaIA debe saber cómo funcionan las herramientas instaladas y futuras sin depender de memoria general del modelo.

Cada herramienta debe tener documentación local mínima.

## Carpeta recomendada

`docs/tools/`

Ejemplos:

- docs/tools/nmap.md
- docs/tools/nuclei.md
- docs/tools/hackrf.md
- docs/tools/android_tools.md
- docs/tools/x4_connector.md
- docs/tools/x5_ojrouter.md
- docs/tools/ollama_mistral.md
- docs/tools/hermes_agent.md

## Formato mínimo por herramienta

Cada documento debe incluir:

- tool_id
- name
- module_ids
- technique_ids
- recommended_version
- installed_version
- runtime
- installation_source
- config_paths
- input_formats
- output_formats
- parser
- evidence_contract
- known_errors
- healthcheck_method
- version_lock_id
- requires_user_implementation
- notes_for_laia

## Herramienta nueva

Cuando se añade una herramienta nueva:

1. Crear wrapper o connector.
2. Crear docs/tools/<tool_id>.md.
3. Añadir VersionLock.
4. Añadir healthcheck.
5. Añadir parser si aplica.
6. Añadir evidence contract.
7. Permitir que LaIA la consulte.
8. Actualizar Knowledge Base.


## Extensión Ronda 0-F — Catálogo Kali/tools

La ingesta de documentación de herramientas debe seguir [KALI_TOOL_KNOWLEDGE_CATALOG.md](KALI_TOOL_KNOWLEDGE_CATALOG.md). Cada ficha futura en `docs/tools/` debe declarar tool_id, URLs oficiales, paquete Kali si aplica, VersionLock, ToolHealth, permisos, formatos, parser, evidence contract, known_errors y notas separadas para LaIA, X5 y Hermes.

Una herramienta documentada o instalada no implica técnica disponible. LaIA debe distinguir tool_available, technique_registered, worker_available, parser_available, evidence_contract_available, permission_allowed, execution_allowed y user_logic_required.
